from __future__ import annotations
from typing import TypedDict, Any, Optional, List, Dict

class AgentState(TypedDict, total=False):
    # inputs
    question: Optional[str]
    schema: Dict[str, Any]
    df: Any

    # planning/execution
    plan: Any
    result: Any
    explanation: Optional[str]
    error: Optional[str]
    retries: int
    confidence: Optional[float]
    charts: List[Any]
    clarification_question: Optional[str]

    # follow-up intelligence
    previous_question: Optional[str]
    previous_plan: Optional[dict]
    is_followup: bool

    # production-ish memory
    memory_summary: Optional[str]

    # meta
    intent: str
    allow_followups: bool
    follow_up_questions: List[str]
