from typing import List, Tuple

import numpy as np
import pandas as pd


def clean_dataframe_mysql(df: pd.DataFrame) -> pd.DataFrame:
    """处理 dataframe 中的缺失值 - MySQL"""
    df = df.copy()
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].apply(lambda x: f"'{x}'" if pd.notnull(x) else x)
    df = df.fillna("Null").replace("", "Null")
    return df

def clean_dataframe_clickhouse(df: pd.DataFrame) -> pd.DataFrame:
    """处理 dataframe 中的缺失值 - ClickHouse"""
    df = df.copy()
    str_cols = df.select_dtypes(include=["object", "string"]).columns
    num_cols = df.columns.difference(str_cols)
    df[str_cols] = df[str_cols].fillna("")
    df[num_cols] = df[num_cols].fillna(0)
    return df


def to_python_values(df: pd.DataFrame) -> List[Tuple]:
    """将 dataframe 转为 Python 原生类型的 tuple 列表，并将 NaN 替换为 None"""
    return [tuple(None if pd.isna(x) else (x.item() if isinstance(x, np.generic) else x) for x in row) for row
            in df.itertuples(index=False, name=None)]
