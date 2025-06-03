import json
from typing import Any

from langchain_community.llms import OpenAI

from ..common import EXTRACT_ISSUE_PROMPT


def parse_issue_summary_response(raw_response: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_response.strip())
        for key in ("reported_issues", "affected_components", "severity"):
            if key not in parsed:
                return {
                    "error": f'Missing key "{key}" in JSON.',
                    "raw_response": raw_response.strip()
                }
        return parsed
    except json.JSONDecodeError:
        return {
            "error": "LLM response was not valid JSON.",
            "raw_response": raw_response.strip()
        }


def issue_summary_tool(issue_text: str) -> dict[str, Any]:
    """Issue summarize tool. Use this tool when summarize a raw issue report."""
    if not issue_text or not issue_text.strip():
        return {"error": "No issue text provided.", "raw_response": ""}

    prompt = EXTRACT_ISSUE_PROMPT.format(issue_text=issue_text)
    llm = OpenAI(temperature=0)

    try:
        raw_response = llm(prompt)
    except Exception as e:
        return {"error": f"LLM call failed: {e}", "raw_response": ""}

    return parse_issue_summary_response(raw_response)