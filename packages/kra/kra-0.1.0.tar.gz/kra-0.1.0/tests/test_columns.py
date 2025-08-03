# Automatically generated with Copilot 
import polars as pl
import pytest
import kra  

def test_apply_lowercase():
    df = pl.DataFrame({"A": [1], "B": [2]})
    result = df.cols.apply(lambda x: x.lower())
    assert result.columns == ["a", "b"]

def test_to_lowercase():
    df = pl.DataFrame({"A": [1], "B": [2]})
    result = df.cols.to_lowercase()
    assert result.columns == ["a", "b"]

def test_to_uppercase():
    df = pl.DataFrame({"a": [1], "b": [2]})
    result = df.cols.to_uppercase()
    assert result.columns == ["A", "B"]

def test_to_titlecase():
    df = pl.DataFrame({"first name": [1], "last name": [2]})
    result = df.cols.to_titlecase()
    assert result.columns == ["First Name", "Last Name"]

def test_to_camelcalse():
    df = pl.DataFrame({"first name": [1], "last name": [2]})
    result = df.cols.to_camelcalse()
    assert result.columns == ["FirstName", "LastName"]

def test_to_snakecase():
    df = pl.DataFrame({"First Name": [1], "Last Name": [2]})
    result = df.cols.to_snakecase()
    assert result.columns == ["first_name", "last_name"]

def test_replace():
    df = pl.DataFrame({"foo-bar": [1], "baz-bar": [2]})
    result = df.cols.replace("-bar", "_suffix")
    assert result.columns == ["foo_suffix", "baz_suffix"]

def test_has_all_true():
    df = pl.DataFrame({"a": [1], "b": [2]})
    has, missing = df.cols.has_all(["a", "b"])
    assert has is True
    assert missing == []

def test_has_all_false():
    df = pl.DataFrame({"a": [1], "b": [2]})
    has, missing = df.cols.has_all(["a", "c"])
    assert has is False
    assert missing == ["c"] or set(missing) == {"c"}

def test_has_any_true():
    df = pl.DataFrame({"a": [1], "b": [2]})
    assert df.cols.has_any(["b", "c"]) is True

def test_has_any_false():
    df = pl.DataFrame({"a": [1], "b": [2]})
    assert df.cols.has_any(["x", "y"]) is False

def test_has_exactly_true():
    df = pl.DataFrame({"a": [1], "b": [2]})
    assert df.cols.has_exactly(["a", "b"]) is True

def test_has_exactly_false():
    df = pl.DataFrame({"a": [1], "b": [2]})
    assert df.cols.has_exactly(["a"]) is False

def test_rename_partial():
    df = pl.DataFrame({"a": [1], "b": [2]})
    result = df.cols.rename({"a": "x", "c": "y"})
    assert result.columns == ["x", "b"]