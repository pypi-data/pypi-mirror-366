# Automatically generated with Copilot 

import polars as pl
import kra  

def test_label_expr_encode():
    df = pl.DataFrame({"animal": ["cat", "dog", "cat"]})
    result = df.with_columns(pl.col("animal").label.encode().alias("encoded"))
    # The encoded column should be [0, 1, 0] or [1, 0, 1] depending on categorical order, but unique values
    encoded = result["encoded"].to_list()
    assert set(encoded) == {0, 1}
    assert encoded[0] == encoded[2]
    assert encoded[0] != encoded[1]

def test_label_series_encode():
    s = pl.Series(["cat", "dog", "cat"])
    encoded = s.label.encode()
    # The encoded series should be [0, 1, 0] or [1, 0, 1] depending on categorical order, but unique values
    values = encoded.to_list()
    assert set(values) == {0, 1}
    assert values[0] == values[2]
    assert values[0] !=