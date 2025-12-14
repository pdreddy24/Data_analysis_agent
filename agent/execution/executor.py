from __future__ import annotations

from typing import Any, Dict

import pandas as pd
import matplotlib.pyplot as plt

from agent.schema.models import AnalysisPlan


def _ensure_index(df: pd.DataFrame) -> pd.DataFrame:
    if "__index__" in df.columns:
        return df
    out = df.reset_index().rename(columns={"index": "__index__"})
    return out


def _coerce_numeric(series: pd.Series) -> pd.Series:
    if series.dtype.kind in "biufc":
        return series

    s = series.astype(str).str.strip()
    s = s.replace({"": None, "nan": None, "None": None, "null": None, "NULL": None})
    s = s.str.replace(",", "", regex=False)
    s = s.str.replace(r"^\$", "", regex=True)
    s = s.str.replace(r"%$", "", regex=True)
    s = s.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    return pd.to_numeric(s, errors="coerce")


def executor_node(state: dict) -> dict:
    df: pd.DataFrame | None = state.get("df")
    plan: AnalysisPlan | None = state.get("plan")

    if df is None:
        state["error"] = "No dataframe available for execution."
        state["confidence"] = float(state.get("confidence", 0.0))
        return state

    if plan is None:
        state["error"] = "No plan available for execution."
        state["confidence"] = float(state.get("confidence", 0.0))
        return state

    task_type = getattr(plan, "task_type", None)

    try:
        if task_type == "data_quality":
            dup = int(df.duplicated().sum())
            schema = {
                "duplicate_rows": dup,
                "row_count": int(len(df)),
                "missing_pct": (df.isna().mean() * 100).round(2).to_dict(),
                "dtypes": df.dtypes.astype(str).to_dict(),
            }
            state["schema"] = schema
            state["explanation"] = "Executed data_quality."
            state["confidence"] = float(state.get("confidence", 1.0))
            return state

        if task_type == "summary":
            cols = plan.metrics or []
            if cols:
                cols = [c for c in cols if c in df.columns]
                if not cols:
                    state["error"] = "No valid metric columns found for summary."
                    return state
                desc = df[cols].describe(include="all").T
            else:
                desc = df.describe(include="all").T

            state["result_df"] = desc
            state["explanation"] = "Executed summary."
            state["confidence"] = float(state.get("confidence", 0.82))
            return state

        if task_type == "aggregation":
            metrics = [c for c in (plan.metrics or []) if c in df.columns]
            groups = [c for c in (plan.group_by or []) if c in df.columns]
            agg = getattr(plan, "agg", "sum")

            if agg != "count" and not metrics:
                state["error"] = "No valid numeric metric columns found for aggregation."
                return state

            work = df.copy()
            for m in metrics:
                work[m] = _coerce_numeric(work[m])

            if groups:
                if agg == "count":
                    result = work.groupby(groups).size().reset_index(name="count")
                else:
                    result = work.groupby(groups)[metrics].agg(agg).reset_index()
            else:
                if agg == "count":
                    result = pd.DataFrame({"count": [len(work)]})
                else:
                    result = work[metrics].agg(agg).to_frame().T

            top_k = getattr(plan, "top_k", None)
            sort_desc = bool(getattr(plan, "sort_desc", True))

            if top_k and agg != "count" and metrics:
                result = result.sort_values(by=metrics[0], ascending=not sort_desc).head(int(top_k))

            state["result_df"] = result
            state["explanation"] = f"Executed aggregation ({agg})."
            state["confidence"] = float(state.get("confidence", 0.86))
            return state

        if task_type == "visualization":
            chart_type = getattr(plan, "chart_type", "bar")
            x = getattr(plan, "x", None)
            y = getattr(plan, "y", None)

            work = df.copy()

            # histogram: only needs y
            if chart_type == "hist":
                if not y or y not in work.columns:
                    state["error"] = "Histogram needs a numeric column. Ask: 'hist <numeric_col>'."
                    return state
                work[y] = _coerce_numeric(work[y])
                fig = plt.figure()
                plt.hist(work[y].dropna())
                plt.title(f"Histogram of {y}")
                state["fig"] = fig
                state["explanation"] = "Executed visualization (hist)."
                state["confidence"] = float(state.get("confidence", 0.9))
                return state

            # create __index__ if requested
            if x == "__index__":
                work = _ensure_index(work)

            if x and x not in work.columns:
                state["error"] = f"Invalid plot column x='{x}' not found in dataset."
                return state
            if not y or y not in work.columns:
                state["error"] = f"Invalid plot column y='{y}' not found in dataset."
                return state

            work[y] = _coerce_numeric(work[y])

            # If line chart and x is datetime-ish, try to parse
            if chart_type == "line" and x and x in work.columns:
                try:
                    work[x] = pd.to_datetime(work[x], errors="ignore")
                except Exception:
                    pass

            # aggregate if group_by provided
            group_by = [c for c in (plan.group_by or []) if c in work.columns]
            if group_by and y:
                agg = getattr(plan, "agg", "sum")
                plot_df = work.groupby(group_by)[y].agg(agg).reset_index()
                x_plot = group_by[0]
            else:
                plot_df = work
                x_plot = x

            fig = plt.figure()
            if chart_type == "line":
                plot_df = plot_df.sort_values(by=x_plot) if x_plot else plot_df
                plt.plot(plot_df[x_plot], plot_df[y])
                plt.title(f"{y} over {x_plot}")
            elif chart_type == "scatter":
                plt.scatter(plot_df[x_plot], plot_df[y])
                plt.title(f"{y} vs {x_plot}")
            else:
                # bar default
                # if too many categories, just plot top 20
                if plot_df[x_plot].nunique() > 20:
                    plot_df = plot_df.head(20)
                plt.bar(plot_df[x_plot].astype(str), plot_df[y])
                plt.xticks(rotation=45, ha="right")
                plt.title(f"{y} by {x_plot}")

            state["fig"] = fig
            state["explanation"] = f"Executed visualization ({chart_type})."
            state["confidence"] = float(state.get("confidence", 0.9))
            return state

        state["error"] = f"Unknown task_type: {task_type}"
        state["confidence"] = float(state.get("confidence", 0.0))
        return state

    except Exception as e:
        # hard fail-safe: never throw to Streamlit
        state["error"] = f"Execution failed: {e}"
        state["confidence"] = 0.0
        return state
