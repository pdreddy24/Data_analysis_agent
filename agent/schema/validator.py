from agent.schema.state import AgentState


def validator_node(state: AgentState) -> AgentState:
    """
    Validate execution results before explanation.
    Sets state['error'] if results are unreliable.
    """

    result = state.get("result")

    if result is None or result.empty:
        state["error"] = "Validation failed: result is empty."
        return state

    if len(result) < 3:
        state["error"] = (
            "Validation warning: result has too few rows "
            "to draw reliable conclusions."
        )
        return state

    numeric_cols = result.select_dtypes(include="number")
    if not numeric_cols.empty:
        if (numeric_cols.isna().all().any()
            or (numeric_cols == 0).all().any()):
            state["error"] = (
                "Validation failed: numeric results contain only zeros or NaNs."
            )
            return state
    return state
