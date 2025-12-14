def generate_explanation(task_type: str, state: dict) -> str:
    if task_type == "schema_audit":
        return (
            "This answer is derived from the preprocessing audit, including "
            "missing value percentages, duplicate detection, dtype conversions, "
            "and dataset shape changes."
        )

    if task_type == "meta_explain":
        return (
            "Confidence is based on deterministic computations, clean aggregation logic, "
            "and the quality of the input dataset. No probabilistic inference was used."
        )

    if task_type == "trend_explain":
        return (
            "Trend analysis is descriptive. Without a time column, patterns are inferred "
            "from distribution changes rather than temporal forecasting."
        )

    return "No explanation available for this analysis."
