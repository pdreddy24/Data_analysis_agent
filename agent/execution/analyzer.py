import pandas as pd
from typing import Dict, Any


def analyze_data(df: pd.DataFrame) -> Dict[str, Any]:
    results = {}
    results["summary"] = df.describe().to_dict()


    if "region" in df.columns and "revenue_usd" in df.columns:
        results["revenue_by_region"] = (
            df.groupby("region")["revenue_usd"]
            .sum()
            .sort_values(ascending=False)
            .to_dict()
        )

    
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] >= 2:
        results["correlation"] = numeric_df.corr().to_dict()

    return results
