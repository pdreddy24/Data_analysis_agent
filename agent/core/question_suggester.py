from typing import List
from agent.schema.state import AgentState

class QuestionSuggester:
    def run(self, state: dict) -> None:
        """
        Generates follow-up questions and stores them in state["follow_up_questions"]
        """

        if not state.get("allow_followups", True):
            return

        intent = state.get("intent", "analysis")

        questions = []

        if intent == "code":
            questions.extend([
                "Do you want this code optimized?",
                "Should I add unit tests?",
                "Do you want this converted into a reusable module?"
            ])

        elif intent == "analysis":
            questions.extend([
                "Do you want a deeper breakdown?",
                "Should I add visualizations?",
                "Do you want this turned into a report?"
            ])

        else:
            questions.extend([
                "Do you want more examples?",
                "Should I simplify this explanation?",
                "Do you want a real-world use case?"
            ])

        state["follow_up_questions"] = questions
