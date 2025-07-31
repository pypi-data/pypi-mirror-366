from collections.abc import Iterator, Mapping, Sequence
from itertools import accumulate
from pathlib import Path
from typing import Optional, no_type_check

import polars as pl
from beartype import beartype
from beartype.door import is_bearable
from polars.io.plugins import register_io_source

from polars_io.common import DEFAULT_BATCH_SIZE, _make_eager
from polars_io.lines import SCAN_LINE_KWARGS

# ways to specify column locations
NameStartEnd = Mapping[str, tuple[int, int]]
NameLength = Sequence[tuple[str | None, int]]  # none as name => discard

ColLocations = NameStartEnd | NameLength


@beartype
@no_type_check
def _standardize_col_locations(locs: ColLocations) -> NameStartEnd:
    if is_bearable(locs, NameStartEnd):
        return locs

    if is_bearable(locs, NameLength):
        names, lengths = zip(*locs)

        locations = [
            (end - length, end) for end, length in zip(accumulate(lengths), lengths)
        ]

        return {name: loc for name, loc in zip(names, locations) if name is not None}


def _extract_columns(
    df: pl.DataFrame,
    col_locations: NameStartEnd,
    *,
    schema: Optional[dict] = None,
    col_subset: Optional[list[str]] = None,
    predicate: Optional[pl.Expr] = None,
    col_name="raw",
) -> pl.DataFrame:
    return (
        df.select(
            pl.col(col_name).str.slice(start, end - start).alias(name)
            for name, (start, end) in col_locations.items()
        )
        .cast(schema or {})
        .select(col_subset or pl.all())
        .filter(*[predicate] if predicate is not None else [])
    )


def scan_fwf(
    file: str | Path,
    cols: ColLocations,
    infer_schema: bool = True,
    infer_schema_length: int = 100,
    **kwargs,
) -> pl.LazyFrame:
    """
    Lazily read from a fixed width file.

    Parameters
    ----------
    file
        The file to read.

    cols
        The locations of the relevant columns in the fixed-width file. Either a mapping from column names to `(start, end)` paris or a sequence of `(name, width)` pairs.

    kwargs
        Other kwargs to pass to [`pl.read_csv_batched`](https://docs.pola.rs/api/python/stable/reference/api/polars.read_csv_batched.html).
    """
    col_locations = _standardize_col_locations(cols)

    read_csv_kwargs = SCAN_LINE_KWARGS | kwargs | dict(new_columns=["raw"])

    if infer_schema:
        # HACK:
        # write a small number of rows to csv and then reread to infer schema
        # hacky, but it works and there doesn't seem to be a better way
        # see: https://github.com/pola-rs/polars/issues/2043
        schema = pl.read_csv(
            pl.read_csv(
                file,
                n_rows=infer_schema_length,
                **read_csv_kwargs,  # type: ignore
            )
            .pipe(_extract_columns, col_locations)
            .write_csv()
            .encode()
        ).schema
    else:
        schema = pl.Schema({col: pl.String for col in col_locations})

    def source_generator(
        with_columns: list[str] | None,
        predicate: pl.Expr | None,
        n_rows: int | None,
        batch_size: int | None,
    ) -> Iterator[pl.DataFrame]:
        reader = pl.read_csv_batched(
            file,
            batch_size=batch_size or DEFAULT_BATCH_SIZE,
            n_rows=n_rows,
            **read_csv_kwargs,  # type: ignore
        )

        while chunks := reader.next_batches(100):
            yield from (
                chunk.pipe(
                    _extract_columns,
                    col_locations,
                    predicate=predicate,
                    col_subset=with_columns,
                    schema=schema,
                )
                for chunk in chunks
            )

    return register_io_source(io_source=source_generator, schema=schema)


read_fwf = _make_eager(scan_fwf)
