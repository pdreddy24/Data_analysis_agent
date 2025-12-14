import pandas as pd
from agent.schema.models import AnalysisPlan


def execute_plan(plan: AnalysisPlan, df: pd.DataFrame) -> pd.DataFrame:
    result_df = df.copy()

    if plan.filters:
        for column, value in plan.filters.items():
            result_df = result_df[result_df[column] == value]

    if plan.task_type in ("breakdown", "aggregation"):
        if not plan.group_by:
            raise ValueError("group_by is required for aggregation tasks")
        aggregation_func = plan.aggregation if hasattr(plan, "aggregation") else "sum"
    
        if aggregation_func not in ["sum", "mean", "count"]:
            raise ValueError(f"Unsupported aggregation function: {aggregation_func}")

        result_df = result_df.groupby(plan.group_by, as_index=False)[plan.metrics].agg(aggregation_func)

    else:
        raise ValueError(f"Unsupported task_type: {plan.task_type}")

    
    if result_df.isnull().values.any():
        result_df = result_df.fillna(0)  

    return result_df
