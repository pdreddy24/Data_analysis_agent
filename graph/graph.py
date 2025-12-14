from __future__ import annotations

from typing import Any, Dict, Literal, Optional

import pandas as pd
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

from agent.core.planner import planner_node
from agent.execution.executor import executor_node


class State(TypedDict, total=False):
    # inputs
    dataset_path: str
    question: Optional[str]
    preview_only: bool
    previous_plan: Optional[dict]

    # working
    df: Optional[pd.DataFrame]
    plan: Any
    confidence: float

    # outputs
    schema: dict
    result_df: Any
    fig: Any
    figure_path: str
    explanation: str

    # error
    error: str

    # final bundle for UI
    result: Dict[str, Any]


def _clean_numeric_like(series: pd.Series) -> pd.Series:
    """
    Convert numeric-looking strings like "18,000" "$1,200" "(300)" to floats.
    Leaves non-numeric columns untouched.
    """
    if series.dtype.kind in "biufc":
        return series

    s = series.astype(str).str.strip()

    # treat obvious null tokens
    s = s.replace({"": None, "nan": None, "None": None, "null": None, "NULL": None})

    # remove commas/currency/percent
    s = s.str.replace(",", "", regex=False)
    s = s.str.replace(r"^\$", "", regex=True)
    s = s.str.replace(r"%$", "", regex=True)

    # parentheses negative: (123) -> -123
    s = s.str.replace(r"^\((.*)\)$", r"-\1", regex=True)

    return pd.to_numeric(s, errors="ignore")


def _auto_type_coerce(df: pd.DataFrame) -> pd.DataFrame:
    """
    Best-effort type cleanup so plots/aggregation don't explode on "18,000".
    Only converts object columns that look mostly numeric.
    """
    out = df.copy()
    for col in out.columns:
        if out[col].dtype == "object":
            cleaned = _clean_numeric_like(out[col])

            # convert if majority became numeric
            numeric_ratio = pd.to_numeric(cleaned, errors="coerce").notna().mean()
            if numeric_ratio >= 0.7:
                out[col] = pd.to_numeric(cleaned, errors="coerce")
            else:
                out[col] = out[col].astype(str)
    return out


class DataLoaderNode:
    def __call__(self, state: State) -> State:
        path = state.get("dataset_path")
        if not path:
            return {"error": "dataset_path missing"}

        try:
            df = pd.read_csv(path)
            df = _auto_type_coerce(df)
            return {"df": df}
        except Exception as e:
            return {"error": f"Failed to load CSV: {e}"}


class SchemaPreviewNode:
    def __call__(self, state: State) -> State:
        df = state.get("df")
        if df is None:
            return {"error": "No df found for schema preview."}

        schema = {
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "row_count": int(len(df)),
            "missing_pct": (df.isna().mean() * 100).round(2).to_dict(),
            "unique_counts": df.nunique(dropna=True).to_dict(),
            "sample_rows": df.head(5).to_dict(orient="records"),
        }

        result = {
            "schema": schema,
            "confidence": 1.0,
            "plan": {"task_type": "preview"},
            "explanation": "Previewed dataset schema.",
        }

        return {
            "schema": schema,
            "confidence": 1.0,
            "result": result,
        }


class PlannerNode:
    def __call__(self, state: State) -> State:
        if state.get("df") is None:
            return {"error": "No dataframe found in state."}

        # normalize question
        q = (state.get("question") or "").strip()
        state["question"] = q

        return planner_node(state)  # returns updated dict


class ExecNode:
    def __call__(self, state: State) -> State:
        return executor_node(state)


class ResponseBuilderNode:
    def __call__(self, state: State) -> State:
        plan = state.get("plan")
        confidence = float(state.get("confidence", 0.0))

        # Always include plan (even on error) so UI can show it
        plan_payload = plan.model_dump() if hasattr(plan, "model_dump") else plan

        if state.get("error"):
            result = {
                "error": state["error"],
                "plan": plan_payload,
                "confidence": confidence,
            }
            return {"result": result}

        result: Dict[str, Any] = {
            "plan": plan_payload,
            "confidence": confidence,
            "explanation": state.get("explanation", f"Executed {getattr(plan, 'task_type', 'task')}."),
        }

        if "schema" in state:
            result["schema"] = state["schema"]
        if "result_df" in state:
            result["result_df"] = state["result_df"]
        if "fig" in state:
            result["fig"] = state["fig"]
        if "figure_path" in state:
            result["figure_path"] = state["figure_path"]

        return {"result": result}


class MemoryUpdateNode:
    def __call__(self, state: State) -> State:
        plan = state.get("plan")
        if plan is None:
            return {}
        plan_dict = plan.model_dump() if hasattr(plan, "model_dump") else plan
        return {"previous_plan": plan_dict}


def route_after_load(state: State) -> Literal["schema_preview", "planner", "respond"]:
    if state.get("error"):
        return "respond"
    if state.get("preview_only"):
        return "schema_preview"
    return "planner"


def route_after_planner(state: State) -> Literal["exec", "respond"]:
    if state.get("error"):
        return "respond"
    return "exec"


def route_after_exec(state: State) -> Literal["respond"]:
    return "respond"


def build_agent_graph():
    builder = StateGraph(State)

    builder.add_node("data_loader", DataLoaderNode())
    builder.add_node("schema_preview", SchemaPreviewNode())
    builder.add_node("planner", PlannerNode())
    builder.add_node("exec", ExecNode())
    builder.add_node("respond", ResponseBuilderNode())
    builder.add_node("memory_update", MemoryUpdateNode())

    builder.add_edge(START, "data_loader")
    builder.add_conditional_edges("data_loader", route_after_load)

    builder.add_edge("schema_preview", END)

    builder.add_conditional_edges("planner", route_after_planner)
    builder.add_conditional_edges("exec", route_after_exec)

    builder.add_edge("respond", "memory_update")
    builder.add_edge("memory_update", END)

    return builder.compile()


app = build_agent_graph()
