from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from agent.core.planner import planner_node
from agent.execution.executor import executor_node


def _schema_preview(df: pd.DataFrame) -> Dict[str, Any]:
    return {
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "row_count": len(df),
        "missing_pct": (df.isna().mean() * 100).round(2).to_dict(),
        "unique_counts": df.nunique(dropna=True).to_dict(),
        "sample_rows": df.head(5).to_dict(orient="records"),
    }


def run_analysis(
    question: Optional[str],
    dataset_path: str,
    preview_only: bool = False,
    previous_plan: Optional[dict] = None,
) -> Dict[str, Any]:
    """
    Main orchestration:
      1) load dataframe
      2) preview schema OR plan intent
      3) execute plan
      4) return UI-friendly payload
    """
    df = pd.read_csv(dataset_path)

    if preview_only:
        return {"schema": _schema_preview(df), "confidence": 1.0}

 
    state: Dict[str, Any] = {
        "question": question,
        "df": df,
        "previous_plan": previous_plan,
    }

    state = planner_node(state)
    if state.get("error"):
        return {"error": state["error"], "confidence": 0.0}

    plan = state["plan"]  # AnalysisPlan

    state = executor_node(state)
    if state.get("error"):
        return {
            "error": state["error"],
            "plan": plan.model_dump(),
            "confidence": float(state.get("confidence", 0.0)),
        }

    confidence = float(state.get("confidence", 0.80))

    explanation = f"Executed {plan.task_type}."
    if getattr(plan, "metrics", None):
        if plan.metrics:
            explanation += f" Metric: {plan.metrics[0]}."
    if getattr(plan, "group_by", None):
        if plan.group_by:
            explanation += f" Grouped by: {plan.group_by[0]}."
    if getattr(plan, "agg", None):
        if plan.agg:
            explanation += f" Aggregation: {plan.agg}."

    out: Dict[str, Any] = {
        "plan": plan.model_dump(),
        "confidence": confidence,
        "explanation": explanation,
    }

    # passthrough artifacts
    if "schema" in state:
        out["schema"] = state["schema"]
    if "result_df" in state:
        out["result_df"] = state["result_df"]
    if "fig" in state:
        out["fig"] = state["fig"]  # Streamlit can render this
    if "figure_path" in state:
        out["figure_path"] = state["figure_path"]  # CLI can use this

    return out
