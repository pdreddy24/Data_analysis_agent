import pandas as pd
from typing import Dict, Any, Tuple


def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:

    log = {}

    
    before = len(df)
    df = df.drop_duplicates()
    log["duplicates_removed"] = before - len(df)
    missing_info = {}
    for col in df.columns:
        if df[col].isna().any():
            if df[col].dtype in ["int64", "float64"]:
                median = df[col].median()
                df[col] = df[col].fillna(median)
                missing_info[col] = f"filled with median ({median})"
            else:
                before = len(df)
                df = df.dropna(subset=[col])
                missing_info[col] = f"dropped {before - len(df)} rows"

    log["missing_values"] = missing_info
    return df, log
