import polars as pl

from kra.utils import Cloneable


@pl.api.register_expr_namespace('label')
class LabelExpr:
    """
    Expression namespace for label encoding in polars expressions.

    Example
    -------
    >>> import polars as pl
    >>> import kra  # noqa: F401, needed for registration
    >>> df = pl.DataFrame({"animal": ["cat", "dog", "cat"]})
    >>> df.with_columns(pl.col("animal").label.encode().alias("encoded"))
    shape: (3, 2)
    ┌────────┬─────────┐
    │ animal ┆ encoded │
    ├────────┼─────────┤
    │ cat    ┆ 0       │
    │ dog    ┆ 1       │
    │ cat    ┆ 0       │
    └────────┴─────────┘
    """

    def __init__(self, expr: pl.Expr) -> None:
        self._expr = expr
    
    def encode(self):
        """
        Encode string values as integer labels using categorical encoding.

        Returns
        -------
        pl.Expr
            An expression that encodes string values as integer labels.

        Examples
        --------
        >>> import polars as pl
        >>> import kra  # noqa: F401
        >>> df = pl.DataFrame({"animal": ["cat", "dog", "cat"]})
        >>> df.with_columns(pl.col("animal").label.encode().alias("encoded"))
        shape: (3, 2)
        ┌────────┬─────────┐
        │ animal ┆ encoded │
        ├────────┼─────────┤
        │ cat    ┆ 0       │
        │ dog    ┆ 1       │
        │ cat    ┆ 0       │
        └────────┴─────────┘
        """
        return self._expr.cast(pl.String).cast(pl.Categorical).to_physical()


@pl.api.register_series_namespace('label')
class LabelSeries:
    """
    Series namespace for label encoding in polars Series.

    Example
    -------
    >>> import polars as pl
    >>> import kra  # noqa: F401, needed for registration
    >>> s = pl.Series(["cat", "dog", "cat"])
    >>> s.label.encode()
    shape: (3,)
    Series: '' [u32]
    [
        0
        1
        0
    ]
    """

    def __init__(self, series: pl.Series) -> None:
        self._series = series
    
    def encode(self):
        """
        Encode string values as integer labels using categorical encoding.

        Returns
        -------
        pl.Series
            A Series with integer labels for each unique string value.

        Examples
        --------
        >>> import polars as pl
        >>> import kra  # noqa: F401
        >>> s = pl.Series(["cat", "dog", "cat"])
        >>> s.label.encode()
        shape: (3,)
        Series: '' [u32]
        [
            0
            1
            0
        ]
        """
        return self._series.cast(pl.String).cast(pl.Categorical).to_physical()
        # d = {k: v for v, k in enumerate(self._series.unique())}
        # return self._series.replace(d, return_dtype=pl.Int32)
        
