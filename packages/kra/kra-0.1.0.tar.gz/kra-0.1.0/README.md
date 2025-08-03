# kra

A set of useful tools to work with [polars](https://pola-rs.github.io/polars/), providing convenient extensions for DataFrame manipulation, column operations, label encoding, and more.

## Installation

Build and install the Rust extension and Python API using [maturin](https://github.com/PyO3/maturin):

```sh
pip install maturin
maturin develop
```

Or, for development and testing:

```sh
pip install nox
nox
```

## Features

- **DataFrame and Series extensions**: Add new methods to polars DataFrames and Series.
- **Column utilities**: Easily rename, check, and transform DataFrame columns.
- **Label encoding**: Encode string labels as categorical/integer values.
- **Dict-of-dicts conversion**: Convert between DataFrames and nested dictionaries.

---

## Example Use Cases

### 1. Dict-of-Dicts Conversion

Convert a DataFrame to a dict of dicts using a column as the key:

```python
import polars as pl
import kra

df = pl.DataFrame({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"]
})

dod = df.to_dod("id")
# {1: {'id': 1, 'name': 'Alice'}, 2: {'id': 2, 'name': 'Bob'}, ...}

# Convert back:
df2 = kra.from_dod(dod, "id")
```

---

### 2. Column Name Transformations

Transform column names to different cases:

```python
import polars as pl
import kra

df = pl.DataFrame({
    "First Name": [1, 2],
    "Last Name": [3, 4]
})

df_lower = df.cols.to_lowercase()
df_camel = df.cols.to_camelcalse()
df_snake = df.cols.to_snakecase()
```

---

### 3. Label Encoding

Encode string labels as integers:

```python
import polars as pl
import kra

df = pl.DataFrame({
    "label": ["cat", "dog", "cat", "bird"]
})

# Series API
encoded = df["label"].label.encode()

# Expression API (for use in with_columns, etc.)
df2 = df.with_columns(
    pl.col("label").label.encode().alias("encoded_label")
)
```

---

### 4. DataFrame Utilities

Drop columns of type Null:

```python
import polars as pl
import kra

df = pl.DataFrame({
    "a": [1, 2, 3],
    "b": [None, None, None]
})

df_clean = df.drop_null_cols()
```

---

### 5. From Array-like

Create a DataFrame from a numpy array:

```python
import kra
import numpy as np

data = np.array([[1, 2], [3, 4]])
df = kra.from_arraylike(data, schema=["x", "y"], orient="col")
```

---

## API Reference

- `kra.from_dod`: Create DataFrame from dict of dicts.
- `kra.to_dod`: Convert DataFrame to dict of dicts.
- `kra.Cols`: DataFrame column utilities (access via `df.cols`).
- `kra.LabelSeries`: Series label encoding (access via `series.label`).
- `kra.LabelExpr`: Expression label encoding (access via `pl.col(...).label`).
- `kra.drop_null_cols`: Remove columns of type Null.
- `kra.from_arraylike`: Create DataFrame from array-like objects.

For more, see the intro.ipynb notebook.

---

## Rust Extension

kra includes a Rust extension for fast label encoding, accessible via the Python API.

---

## License

MIT License. See LICENSE for details.