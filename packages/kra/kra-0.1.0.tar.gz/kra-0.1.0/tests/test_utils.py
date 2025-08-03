# Automatically generated with Copilot

import polars as pl
import numpy as np
import kra  # noqa: F401

def test_to_dod():
    df = pl.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
    result = df.to_dod("id")
    assert result == {1: {'id': 1, 'name': 'Alice'}, 2: {'id': 2, 'name': 'Bob'}}

def test_from_dod():
    dod = {1: {"name": "Alice"}, 2: {"name": "Bob"}}
    df = pl.from_dod(dod, "id")
    assert set(df.columns) == {"id", "name"}
    assert set(df["id"].to_list()) == {1, 2}
    assert set(df["name"].to_list()) == {"Alice", "Bob"}

def test_from_arraylike():
    data = np.array([[1, 2, 3], [4, 5, 6]])
    df = pl.from_arraylike(data, schema=["a", "b"], orient="col")
    assert df.shape == (3, 2)
    assert set(df.columns) == {"a", "b"}
    assert df["a"].to_list() == [1, 2, 3]
    assert df["b"].to_list() == [4, 5, 6]

def test_from_memoryview():
    data = np.array([[1, 2], [3, 4]])
    mv = memoryview(data)
    df = pl.from_memoryview(mv, schema=["x", "y"], orient="col")
    assert set(df.columns) == {"x", "y"}
    assert df["x"].to_list() == [1, 3]
    assert df["y"].to_list() == [2, 4]

def test_maybe_col_exists():
    df = pl.DataFrame({"a": [1, 2]})
    result = df.select(kra.maybe_col("a", 0))
    assert result["a"].to_list() == [1, 2]

def test_maybe_col_missing():
    df = pl.DataFrame({"a": [1, 2]})
    result = df.select(kra.maybe_col("b", 0))
    assert result["b"].to_list() == [0, 0]

def test_split_entries_by():
    df = pl.DataFrame({"a": [1, 2], "n": [2, 3]})
    result = df.split_entries_by("n")
    assert set(result.columns) == {"a", "n"}
    assert result.shape[0] == 5

def test_to_dicts():
    df = pl.DataFrame({"g": ["a", "a", "b"], "x": [1, 2, 3]})
    d = df.groupby("g").to_dicts()
    assert set(d.keys()) == {"a", "b"}
    assert all(isinstance(v, list) for v in d.values())
    assert d["a"][0]["g"] == "a"

def test_to_set():
    s = pl.Series([1, 2, 2, 3])
    result = s.to_set()
    assert result
