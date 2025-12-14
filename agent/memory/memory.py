from typing import Dict


class ConversationMemory:
    def __init__(self):
        self._store = {}

    def load(self, session_id: str) -> dict:
        return self._store.get(session_id, {})

    def save(self, session_id: str, state: dict) -> None:
        self._store[session_id] = {
            "previous_question": state.get("question"),
            "previous_plan": state.get("plan"),
            "previous_result": state.get("result"),
        }
