
import polars as pl
import polars.dataframe.group_by as plg 

# TODO: add optional name argument

def extend_polars_dataframe(fun: callable):
    """Decorator to extend polars DataFrame API"""
    setattr(pl.DataFrame, fun.__name__, fun)
    return fun # Needed?

def extend_polars_group_by(fun: callable):
    """Decorator to extend polars DataFrame API"""
    setattr(plg.GroupBy, fun.__name__, fun)
    return fun # Needed?

def extend_polars(fun: callable):
    """Decorator to extend polars DataFrame API"""
    setattr(pl, fun.__name__, fun)
    return fun

def extend_polars_series(fun: callable):
    """Decorator to extend polars Series API"""
    setattr(pl.Series, fun.__name__, fun)
    return fun 
