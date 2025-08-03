import polars as pl
from kra.utils import extend_polars_dataframe


@extend_polars_dataframe
def drop_null_cols(df: pl.DataFrame) -> pl.DataFrame:
    """
    Exclude columns of type Null from the DataFrame.

    Returns
    -------
    pl.DataFrame
        DataFrame with all columns of type Null removed.

    Examples
    --------
    >>> import polars as pl
    >>> import kra 
    >>> df = pl.DataFrame({"a": [1, 2], "b": [None, None]})
    >>> df.drop_null_cols()
    shape: (2, 1)
    ┌─────┐
    │ a   │
    ├─────┤
    │ 1   │
    │ 2   │
    └─────┘
    """
    return df.with_columns(pl.exclude(pl.Null))

@extend_polars_dataframe
def fork(df: pl.DataFrame, new_dfs: list) -> list[pl.DataFrame]:
    """
    Fork a DataFrame into multiple new DataFrames with additional columns.

    Parameters
    ----------
    new_dfs : list of dict
        Each dict specifies new columns to add to a forked DataFrame.

    Returns
    -------
    list of pl.DataFrame
        List of new DataFrames, each with the specified additional columns.

    Examples
    --------
    >>> import polars as pl
    >>> import kra  
    >>> df = pl.DataFrame({"a": [1, 2]})
    >>> forks = df.fork([{"b": [10, 20]}, {"c": [100, 200]}])
    >>> for f in forks:
    ...     print(f)
    shape: (2, 2)
    ┌─────┬─────┐
    │ a   ┆ b   │
    ├─────┼─────┤
    │ 1   ┆ 10  │
    │ 2   ┆ 20  │
    └─────┴─────┘
    shape: (2, 2)
    ┌─────┬───────┐
    │ a   ┆ c     │
    ├─────┼───────┤
    │ 1   ┆ 100   │
    │ 2   ┆ 200   │
    └─────┴───────┘
    """
    # TODO: 
    return [df.with_columns(**n) for n in new_dfs]
