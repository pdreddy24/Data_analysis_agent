from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from typing import Dict, Any

def interpret_results(question: str, analysis: dict) -> str:
    prompt = PromptTemplate(
        template="""
You are a senior data analyst.

User question:
{question}

Analysis results:
{analysis}

Explain the key findings clearly.
- No speculation
- Only insights supported by data
- Business-friendly language
""",
        input_variables=["question", "analysis"]
    )

    llm = ChatOpenAI(temperature=0)
    response = llm.invoke(
        prompt.format(question=question, analysis=analysis)
    )

    return response.content
