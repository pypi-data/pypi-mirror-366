# Automatically generated with Copilot 

import polars as pl
import kra 

def test_drop_null_cols_removes_null_column():
    df = pl.DataFrame({"a": [1, 2], "b": [None, None]})
    result = df.drop_null_cols()
    assert result.columns == ["a"]
    assert "b" not in result.columns

def test_drop_null_cols_keeps_non_null():
    df = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
    result = df.drop_null_cols()
    assert result.columns == ["a", "b"]

def test_fork_creates_multiple_dataframes():
    df = pl.DataFrame({"a": [1, 2]})
    forks = df.fork([{"b": [10, 20]}, {"c": [100, 200]}])
    assert len(forks) == 2
    assert forks[0].columns == ["a", "b"]
    assert forks[1].columns == ["a", "c"]
    assert forks[0]["b"].to_list() == [10, 20]
    assert forks[1]["c"].to_list()