import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any


class DatasetLoadError(Exception):
    """Raised when dataset loading or profiling fails."""

def load_dataset(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Load a dataset from CSV or Parquet and return (df, schema).

    Guarantees:
    - Fails fast on invalid inputs
    - Never mutates data
    - Provides lightweight profiling for downstream agents
    """
    if not file_path:
        raise DatasetLoadError("No dataset path provided")

    path = Path(file_path)

    if not path.exists():
        raise DatasetLoadError(f"Dataset not found at: {file_path}")

    if not path.is_file():
        raise DatasetLoadError(f"Provided path is not a file: {file_path}")

    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        elif path.suffix.lower() in {".parquet", ".pq"}:
            df = pd.read_parquet(path)
        else:
            raise DatasetLoadError(
                "Unsupported file format. Only CSV and Parquet are supported."
            )
    except Exception as e:
        raise DatasetLoadError(f"Failed to load dataset: {str(e)}") from e

    if df.empty:
        raise DatasetLoadError("Loaded dataset is empty")

    if df.columns.duplicated().any():
        raise DatasetLoadError("Dataset contains duplicate column names")

    try:
        missing_pct = {
            col: float(df[col].isna().mean())
            for col in df.columns
        }

        unique_counts = {
            col: int(df[col].nunique(dropna=True))
            for col in df.columns
        }
    except Exception as e:
        raise DatasetLoadError(f"Failed during dataset profiling: {str(e)}") from e

    schema: Dict[str, Any] = {
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "row_count": int(len(df)),
        "missing_pct": missing_pct,
        "unique_counts": unique_counts,
        "sample_rows": df.head(5).to_dict(orient="records"),
    }

    return df, schema
