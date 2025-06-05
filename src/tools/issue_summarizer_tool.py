from typing import Any
from langchain_openai import OpenAI
import json

from ..common.prompt import EXTRACT_ISSUE_PROMPT


def issue_summary_tool(issue_text: str) -> dict[str, Any]:
    """
    Summarize a raw issue report into structured fields:
    - reported_issues
    - affected_components
    - severity
    """
    if not issue_text.strip():
        return {"error": "No issue text provided.", "raw_response": ""}
    prompt = EXTRACT_ISSUE_PROMPT.format(issue_text=issue_text.strip())
    llm = OpenAI(temperature=0)
    raw_response = llm(prompt)
    try:
        cleaned_response = raw_response.replace("\n", "").replace("\r", "")
        parsed = json.loads(cleaned_response)

        return parsed

    except Exception as e:
        return {"error": e, "raw_response": raw_response}
