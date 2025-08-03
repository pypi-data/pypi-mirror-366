import polars as pl
import re

from kra.utils import Cloneable


@pl.api.register_dataframe_namespace('cols')
class Cols(Cloneable):
    """
    A namespace for convenient DataFrame column operations.

    Access via `df.cols` for any polars DataFrame.

    Provides methods for:
      - Bulk renaming and transforming column names (case, pattern, etc.)
      - Checking for presence of columns
      - Safe renaming with partial mappings

    Example
    --------
    >>> import polars as pl
    >>> import kra
    >>> df = pl.DataFrame({"First Name": [1], "Last Name": [2]})
    >>> df.cols.to_snakecase()
    shape: (1, 2)
    ┌────────────┬───────────┐
    │ first_name ┆ last_name │
    └────────────┴───────────┘
    """

    def apply(self, fun: callable, in_place: bool = False):
        """
        Apply a function to all column names.

        Parameters
        ----------
        fun : callable
            Function to apply to each column name.
        in_place : bool, default False
            If True, modify the DataFrame in place. If False, return a copy.

        Returns
        -------
        pl.DataFrame
            DataFrame with transformed column names.

        Examples
        --------
        >>> df = pl.DataFrame({"A": [1], "B": [2]})
        >>> df.cols.apply(lambda x: x.lower())
        shape: (1, 2)
        ┌─────┬─────┐
        │ a   ┆ b   │
        └─────┴─────┘
        """
        df = self._clone_if(in_place)
        df.columns = [fun(x) for x in df.columns]
        return df 
    
    def to_lowercase(self, in_place: bool = False):
        """
        Convert all column names to lowercase.

        Parameters
        ----------
        in_place : bool, default False
            If True, modify in place. If False, return a copy.

        Returns
        -------
        pl.DataFrame
            DataFrame with lowercase column names.

        Examples
        --------
        >>> df = pl.DataFrame({"A": [1], "B": [2]})
        >>> df.cols.to_lowercase()
        shape: (1, 2)
        ┌─────┬─────┐
        │ a   ┆ b   │
        └─────┴─────┘
        """
        return self.apply(lambda x: x.lower(), in_place=in_place)
    
    def to_uppercase(self, in_place: bool = False):
        """
        Convert all column names to uppercase.

        Parameters
        ----------
        in_place : bool, default False
            If True, modify in place. If False, return a copy.

        Returns
        -------
        pl.DataFrame
            DataFrame with uppercase column names.

        Examples
        --------
        >>> df = pl.DataFrame({"a": [1], "b": [2]})
        >>> df.cols.to_uppercase()
        shape: (1, 2)
        ┌─────┬─────┐
        │ A   ┆ B   │
        └─────┴─────┘
        """
        return self.apply(lambda x: x.upper(), in_place=in_place)
    
    def to_titlecase(self, in_place: bool = False):
        """
        Convert all column names to title case.

        Parameters
        ----------
        in_place : bool, default False
            If True, modify in place. If False, return a copy.

        Returns
        -------
        pl.DataFrame
            DataFrame with title-cased column names.

        Examples
        --------
        >>> df = pl.DataFrame({"first name": [1], "last name": [2]})
        >>> df.cols.to_titlecase()
        shape: (1, 2)
        ┌────────────┬───────────┐
        │ First Name ┆ Last Name │
        └────────────┴───────────┘
        """
        return self.apply(lambda x: x.title(), in_place=in_place)
    
    def to_camelcalse(self, in_place: bool = False):
        """
        Convert all column names to camel case.

        Parameters
        ----------
        in_place : bool, default False
            If True, modify in place. If False, return a copy.

        Returns
        -------
        pl.DataFrame
            DataFrame with camelCase column names.

        Examples
        --------
        >>> df = pl.DataFrame({"first name": [1], "last name": [2]})
        >>> df.cols.to_camelcalse()
        shape: (1, 2)
        ┌──────────┬─────────┐
        │ FirstName┆ LastName│
        └──────────┴─────────┘
        """
        fun = lambda x: ''.join(word for word in x.title() if not x.isspace())
        return self.apply(fun, in_place=in_place)

    def to_snakecase(self, in_place: bool = False):
        """
        Convert all column names to snake_case.

        Parameters
        ----------
        in_place : bool, default False
            If True, modify in place. If False, return a copy.

        Returns
        -------
        pl.DataFrame
            DataFrame with snake_case column names.

        Examples
        --------
        >>> df = pl.DataFrame({"First Name": [1], "Last Name": [2]})
        >>> df.cols.to_snakecase()
        shape: (1, 2)
        ┌────────────┬───────────┐
        │ first_name ┆ last_name │
        └────────────┴───────────┘
        """
        fun = lambda x: re.sub('\\s', '', re.sub(r'(?<!^)(?=[A-Z])', '_', x)).lower()
        return self.apply(fun, in_place=in_place)
    
    def replace(self, pattern: str | re.Pattern, repl: str, in_place: bool = False):
        """
        Replace a regex pattern in all column names.

        Parameters
        ----------
        pattern : str or re.Pattern
            Pattern to search for.
        repl : str
            Replacement string.
        in_place : bool, default False
            If True, modify in place. If False, return a copy.

        Returns
        -------
        pl.DataFrame
            DataFrame with replaced column names.

        Examples
        --------
        >>> df = pl.DataFrame({"foo-bar": [1], "baz-bar": [2]})
        >>> df.cols.replace("-bar", "_suffix")
        shape: (1, 2)
        ┌──────────┬────────────┐
        │ foo_suffix ┆ baz_suffix │
        └──────────┴────────────┘
        """
        return self.apply(lambda x: re.sub(pattern, repl, x), in_place=in_place)
    
    def has_all(self, columns: list[str], return_missing: bool = True) -> bool | tuple[bool, list[str]]:
        """
        Check if all specified columns are present in the DataFrame.

        Parameters
        ----------
        columns : list of str
            List of column names to check.
        return_missing : bool, default True
            If True, also return a list of missing columns.

        Returns
        -------
        bool or (bool, list of str)
            True if all columns are present, otherwise False.
            If return_missing is True, also returns a list of missing columns.

        Examples
        --------
        >>> df = pl.DataFrame({"a": [1], "b": [2]})
        >>> df.cols.has_all(["a", "b"])
        (True, [])
        >>> df.cols.has_all(["a", "c"])
        (False, ['c'])
        """
        missing = self._missing_cols(columns)
        if return_missing:
            return len(missing) == 0, missing
        return len(missing) == 0
    
    def has_any(self, columns: list[str]) -> bool:
        """
        Check if any of the specified columns are present in the DataFrame.

        Parameters
        ----------
        columns : list of str
            List of column names to check.

        Returns
        -------
        bool
            True if any column is present, otherwise False.

        Examples
        --------
        >>> df = pl.DataFrame({"a": [1], "b": [2]})
        >>> df.cols.has_any(["b", "c"])
        True
        >>> df.cols.has_any(["x", "y"])
        False
        """
        return len(self._common_cols(columns)) > 0
    
    def has_exactly(self, columns: list[str]) -> bool:
        """
        Check if the DataFrame has exactly the specified columns (no more, no less).

        Parameters
        ----------
        columns : list of str
            List of column names to check.

        Returns
        -------
        bool
            True if the DataFrame has exactly these columns, otherwise False.

        Examples
        --------
        >>> df = pl.DataFrame({"a": [1], "b": [2]})
        >>> df.cols.has_exactly(["a", "b"])
        True
        >>> df.cols.has_exactly(["a"])
        False
        """
        return set(columns) == set(self._df.columns)
    
    def rename(self, mapping: dict[str, str]) -> pl.DataFrame:
        """
        Rename columns using a mapping, skipping keys not present in the DataFrame.
        A non-strict version of DataFrame.rename() method.
        It skips missing keys without raising an error.

        Parameters
        ----------
        mapping : dict of str to str
            Mapping from old column names to new names.

        Returns
        -------
        pl.DataFrame
            DataFrame with renamed columns.

        Examples
        --------
        >>> df = pl.DataFrame({"a": [1], "b": [2]})
        >>> df.cols.rename({"a": "x", "c": "y"})
        shape: (1, 2)
        ┌─────┬─────┐
        │ x   ┆ b   │
        └─────┴─────┘
        """
        mapping = {k:v for k, v in mapping.items() if k in self._df.columns}
        return self._df.rename(mapping)
                 
    def _common_cols(self, columns: list[str]):
        return set(columns).intersection(set(self._df.columns))

    def _missing_cols(self, columns: list[str]):
        return set(columns).difference(set(self._df.columns))