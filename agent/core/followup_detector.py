def is_followup(question: str) -> bool:
    markers = [
        "what about",
        "why",
        "explain",
        "extend",
        "compare",
        "drill",
        "that",
        "those",
        "earlier",
        "previous"
    ]
    q = question.lower()
    return any(m in q for m in markers)
