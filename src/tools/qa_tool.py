from typing import Any
from langchain_openai import OpenAI
import json

from ..common.prompt import ANSWER_QUESTION_PROMPT


def answer_question_tool(question: str, information: str) -> dict[str, Any]:
    """Generate a concise, developer-focused answer to a question using the provided context."""
    if not question.strip():
        return {"error": "No question provided.", "raw_response": ""}

    prompt = ANSWER_QUESTION_PROMPT.format(
        question=question.strip(), information=information.strip()
    )
    llm = OpenAI(temperature=0)
    raw_response = llm(prompt)
    try:
        parsed = json.loads(raw_response)
        return parsed

    except Exception as e:
        return {"error": e, "raw_response": raw_response}
