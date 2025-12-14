
import os
import matplotlib.pyplot as plt
import pandas as pd
from agent.schema.state import AgentState
from agent.schema.models import AnalysisPlan


def _select_chart_type(plan: AnalysisPlan, df: pd.DataFrame) -> str:
    """
    Decide chart type deterministically.
    """
    if "date" in plan.group_by:
        return "line"
    return "bar"


def visualizer_node(state: AgentState) -> AgentState:
    """
    Create visual artifacts based on analysis plan + result.
    Visualization is deterministic and intent-aware.
    """

    result = state.get("result")
    plan: AnalysisPlan | None = state.get("plan")
    charts: list[str] = []

    if result is None or result.empty or plan is None:
        state["charts"] = charts
        return state

    os.makedirs("outputs/charts", exist_ok=True)

    try:
        numeric_cols = result.select_dtypes(include="number").columns.tolist()
        non_numeric_cols = result.select_dtypes(exclude="number").columns.tolist()

        if not non_numeric_cols or not numeric_cols:
            state["charts"] = charts
            return state

        x = non_numeric_cols[0]
        y_cols = numeric_cols
        chart_type = _select_chart_type(plan, result)

        plt.figure(figsize=(10, 5))
        if len(y_cols) == 1:
            y = y_cols[0]

            if chart_type == "line":
                plt.plot(result[x], result[y], marker="o")
            else:
                plt.bar(result[x].astype(str), result[y])

            plt.ylabel(y)
        else:
            for y in y_cols:
                plt.plot(result[x], result[y], marker="o", label=y)
            plt.legend()

        plt.xlabel(x)
        plt.title(f"{plan.agg.upper()} metrics by {x}")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()

        filename = f"{x}_metrics_chart.png"
        path = os.path.join("outputs/charts", filename)
        plt.savefig(path)
        plt.close()

        charts.append(path)

    except Exception as e:
        state["error"] = f"Visualization error: {str(e)}"

    state["charts"] = charts
    return state
