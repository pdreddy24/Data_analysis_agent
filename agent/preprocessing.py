import pandas as pd
from typing import Dict, Any


def preprocess_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Cleans the dataset and returns:
    - cleaned dataframe
    - data quality report
    - cleaning audit log
    """
    audit_log = []
    original_shape = df.shape
    df = df.copy()
    original_columns = list(df.columns)
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    if list(df.columns) != original_columns:
        audit_log.append("Normalized column names (lowercase, underscores).")
    before = len(df)
    df = df.dropna(how="all")
    dropped = before - len(df)
    if dropped > 0:
        audit_log.append(f"Dropped {dropped} fully empty rows.")

    for col in df.columns:
        if "date" in col:
            before_na = df[col].isna().sum()
            df[col] = pd.to_datetime(df[col], errors="coerce")
            after_na = df[col].isna().sum()
            if after_na > before_na:
                audit_log.append(f"Parsed '{col}' as datetime (invalid values set to NaT).")
            else:
                audit_log.append(f"Parsed '{col}' as datetime.")

    for col in df.columns:
        if df[col].dtype == "object":
            cleaned = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("$", "", regex=False)
                .str.replace("₹", "", regex=False)
                .str.replace("%", "", regex=False)
                .replace({"nan": None, "None": None, "": None})
            )
            converted = pd.to_numeric(cleaned, errors="ignore")
            if converted.dtype != df[col].dtype:
                df[col] = converted
                audit_log.append(f"Converted '{col}' to numeric where possible.")

    quality_report = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "duplicates": int(df.duplicated().sum()),
        "null_percent": ((df.isna().sum() / max(len(df), 1)) * 100).round(2).to_dict(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "shape_change": {
            "before": list(original_shape),
            "after": list(df.shape),
        },
    }

    if quality_report["duplicates"] > 0:
        audit_log.append(f"Detected {quality_report['duplicates']} duplicate rows.")

    if not audit_log:
        audit_log.append("No cleaning actions were necessary.")

    return {
        "df": df,
        "quality_report": quality_report,
        "audit_log": audit_log,
    }
