from langchain_community.llms import OpenAI
from typing import Any
from common import ANSWER_QUESTION_PROMPT

def answer_question_tool(question: str, information: str) -> dict[str, Any]:
    """
    Generate a concise, developer‐focused answer to a question using the provided context.

    Args:
        question (str): The user’s question.
        information (str): Relevant context or data to inform the answer.

    Returns:
        Dict[str, Any]:
            • On success: {"answer": "<generated answer>"}
            • On failure: {"error": "<error message>", "raw_response": "<LLM output if applicable>"}
    """
    if not question.strip():
        return {"error": "No question provided.", "raw_response": ""}

    prompt = ANSWER_QUESTION_PROMPT.format(
        question=question.strip(),
        information=information.strip()
    )
    llm = OpenAI(temperature=0)

    try:
        raw_response = llm(prompt)
    except Exception as e:
        return {"error": f"LLM call failed: {e}", "raw_response": ""}

    return {"answer": raw_response.strip()}
