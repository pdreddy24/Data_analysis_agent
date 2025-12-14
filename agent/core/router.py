def route_after_execution(state):
    """
    Decide next step after execution.
    Routers must NOT raise exceptions.
    """

    if state.get("error"):
        if state.get("retries", 0) < 1:
            state["retries"] = state.get("retries", 0) + 1
            return "replanner"

        return "explainer"

    return "explainer"
