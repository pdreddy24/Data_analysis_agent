from __future__ import annotations

import re
from typing import Optional, Tuple

import pandas as pd
from agent.schema.models import AnalysisPlan



def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower().replace("_", " "))


def _tokenize(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", _norm(s)))


def _score_col_match(question: str, col: str) -> int:
    """
    Score how well `col` matches `question`.
    Higher is better.
    """
    qn = _norm(question)
    cn = _norm(col)

    score = 0

    # Exact phrase present is strongest
    if cn and cn in qn:
        score += 100

    # Token overlap (robust to small formatting differences)
    qt = _tokenize(qn)
    ct = _tokenize(cn)
    overlap = len(qt & ct)
    score += overlap * 10

    # Bonus: common patterns like "by <col>", "of <col>", etc.
    if re.search(rf"\bby\s+{re.escape(cn)}\b", qn):
        score += 40
    if re.search(rf"\bof\s+{re.escape(cn)}\b", qn):
        score += 20

    return score


def _best_col_match(
    question: str,
    df: pd.DataFrame,
    prefer_numeric: bool = False,
    prefer_categorical: bool = False,
    min_score: int = 20,
) -> Optional[str]:
    """
    Pick the best column match from df.columns for the given text.
    - prefer_numeric: only numeric candidates
    - prefer_categorical: only categorical candidates (object/category/bool)
    """
    candidates = df.columns.tolist()

    if prefer_numeric:
        candidates = df.select_dtypes(include="number").columns.tolist()
    elif prefer_categorical:
        candidates = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    if not candidates:
        return None

    scored: list[Tuple[int, str]] = []
    for c in candidates:
        scored.append((_score_col_match(question, c), c))

    scored.sort(reverse=True, key=lambda x: x[0])
    best_score, best_col = scored[0]

    return best_col if best_score >= min_score else None


def _has_word(q: str, word: str) -> bool:
    return re.search(rf"\b{re.escape(word)}\b", q) is not None


def _first_numeric(df: pd.DataFrame) -> Optional[str]:
    nums = df.select_dtypes(include="number").columns.tolist()
    return nums[0] if nums else None


def _first_categorical(df: pd.DataFrame) -> Optional[str]:
    cats = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    return cats[0] if cats else None


def _guess_group_by(question: str, df: pd.DataFrame) -> Optional[str]:
    q = question.strip()

    # explicit "by <something>"
    m = re.search(r"\bby\s+([a-zA-Z0-9_ ]+)$", q.strip().lower())
    if m:
        tail = m.group(1).strip()
        best = _best_col_match(tail, df, prefer_categorical=True)
        if best:
            return best

    # column mention anywhere in question
    best = _best_col_match(q, df, prefer_categorical=True)
    if best:
        return best

    # fallback: first categorical
    return _first_categorical(df)


def _guess_metric(question: str, df: pd.DataFrame) -> Optional[str]:
    q = question.strip().lower()

    # if user mentions a numeric column name anywhere, pick it
    best = _best_col_match(question, df, prefer_numeric=True)
    if best:
        return best

    # keyword-based fallback (but still resolves dynamically)
    if any(k in q for k in ["revenue", "sales", "amount", "value", "profit", "total"]):
        for key in ["revenue", "sales", "amount", "value", "profit", "total"]:
            c = _best_col_match(key, df, prefer_numeric=True, min_score=10)  # slightly looser here
            if c:
                return c

    # final fallback: first numeric
    return _first_numeric(df)


def _guess_date_col(df: pd.DataFrame) -> Optional[str]:
    # name-based first
    for key in ["date", "timestamp", "time", "datetime"]:
        c = _best_col_match(key, df, prefer_categorical=False, min_score=10)
        if c:
            return c

    # dtype-based fallback (if parsed upstream)
    for col in df.columns:
        if "datetime" in str(df[col].dtype).lower():
            return col

    return None


def planner_node(state: dict) -> dict:
    question = (state.get("question") or "").strip()
    q = question.lower()
    df: pd.DataFrame | None = state.get("df")
    previous_plan = state.get("previous_plan")

    if df is None:
        state["error"] = "No dataframe found in state."
        return state

    # META / CONFIDENCE
    if any(k in q for k in ["how confident", "confidence", "are you confident"]):
        state["plan"] = AnalysisPlan(task_type="data_quality")
        state["confidence"] = 1.0
        return state

    # VISUALIZATION / GROWTH / TREND
    viz_hits = any(k in q for k in [
        "plot", "chart", "graph", "visualize", "visualization",
        "bar", "line", "scatter", "hist", "histogram",
        "growth", "trend", "over time", "time series", "timeseries", "timeline", "increase"
    ])

    if viz_hits:
        metric = _guess_metric(question, df)
        group_by = _guess_group_by(question, df)

        # decide chart type
        chart_type = "bar"
        if any(k in q for k in ["growth", "trend", "over time", "time series", "timeseries", "timeline"]):
            chart_type = "line"
        elif "line" in q:
            chart_type = "line"
        elif "scatter" in q:
            chart_type = "scatter"
        elif "hist" in q or "histogram" in q:
            chart_type = "hist"

        # x-axis logic (never invent "index"; use "__index__" which executor can create)
        x = group_by
        if chart_type == "line":
            date_col = _guess_date_col(df)
            x = date_col if date_col else "__index__"

        # histogram doesn't need x; but keep something safe
        if chart_type == "hist":
            x = None

        # If metric is still None, we must fail fast with a useful message
        if chart_type != "hist" and not metric:
            state["error"] = "No numeric column found to plot. Ask like: 'plot <numeric_col> by <group_col>'."
            state["confidence"] = 0.0
            return state

        state["plan"] = AnalysisPlan(
            task_type="visualization",
            metrics=[metric] if metric else [],
            group_by=[group_by] if group_by else [],
            agg="sum",
            sort_desc=True,
            chart_type=chart_type,
            x=x,
            y=metric,
        )
        state["confidence"] = 0.88 if ("growth" in q or "trend" in q) else 0.90
        return state

    # VOLATILITY / STD
    if any(k in q for k in ["volatility", "how volatile", "standard deviation", "std"]):
        metric = _guess_metric(question, df)
        group_by = _guess_group_by(question, df)

        if previous_plan:
            plan = AnalysisPlan(**previous_plan) if isinstance(previous_plan, dict) else previous_plan
        else:
            plan = AnalysisPlan(
                task_type="aggregation",
                metrics=[metric] if metric else [],
                group_by=[group_by] if group_by else [],
                agg="std",
            )

        plan.task_type = "aggregation"
        plan.agg = "std"
        if metric:
            plan.metrics = [metric]
        if group_by:
            plan.group_by = [group_by]

        state["plan"] = plan
        state["confidence"] = 0.95
        return state

    # DATA QUALITY
    data_quality_hits = (
        any(k in q for k in ["missing", "null", "empty", "duplicate", "duplicates", "cleaning", "audit", "outlier"])
        or "dtype" in q
        or "data type" in q
        or (_has_word(q, "na") or _has_word(q, "n/a"))
        or ("column" in q and _has_word(q, "type"))
    )
    if data_quality_hits:
        state["plan"] = AnalysisPlan(task_type="data_quality")
        state["confidence"] = 1.0
        return state

    # TOP-K
    if any(k in q for k in ["top", "highest", "largest", "biggest", "best", "rank"]):
        metric = _guess_metric(question, df)
        group_by = _guess_group_by(question, df)

        top_k = 5
        m = re.search(r"\btop\s+(\d+)\b", q)
        if m:
            try:
                top_k = int(m.group(1))
            except Exception:
                top_k = 5

        state["plan"] = AnalysisPlan(
            task_type="aggregation",
            metrics=[metric] if metric else [],
            group_by=[group_by] if group_by else [],
            agg="sum",
            top_k=top_k,
            sort_desc=True,
        )
        state["confidence"] = 0.92
        return state

    # STANDARD AGGREGATION
    if any(k in q for k in ["total", "sum", "average", "avg", "mean", "min", "max", "count"]):
        metric = _guess_metric(question, df)
        group_by = _guess_group_by(question, df)

        agg = "sum"
        if "average" in q or "avg" in q or "mean" in q:
            agg = "mean"
        elif "min" in q:
            agg = "min"
        elif "max" in q:
            agg = "max"
        elif "count" in q:
            agg = "count"

        state["plan"] = AnalysisPlan(
            task_type="aggregation",
            metrics=[metric] if (metric and agg != "count") else [],
            group_by=[group_by] if group_by else [],
            agg=agg,
            sort_desc=True,
        )
        state["confidence"] = 0.86
        return state

    # SUMMARY
    if any(k in q for k in ["summary", "describe", "stats", "statistics", "distribution"]):
        metric = _guess_metric(question, df)
        state["plan"] = AnalysisPlan(task_type="summary", metrics=[metric] if metric else [])
        state["confidence"] = 0.82
        return state

    # FAIL SAFE
    state["error"] = "Could not infer analysis intent from question."
    state["confidence"] = 0.0
    return state
