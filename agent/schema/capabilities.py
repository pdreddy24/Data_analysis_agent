import pandas as pd


def infer_dataset_capabilities(df: pd.DataFrame):
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    categorical_columns = df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    return {
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "row_count": len(df),
        "unique_counts": {
            col: df[col].nunique() for col in df.columns
        },
    }
