import json
from typing import Any
from langchain_community.llms import OpenAI


def create_issue_summary_prompt(issue_text: str) -> str:
    """
    Build the prompt that instructs the LLM to extract:
      1. reported_issues (list of strings)
      2. affected_components (list of strings)
      3. severity (single string from Low/Medium/High/Critical)

    Returns:
        A string prompt ready for the LLM.
    """
    template = """You are an AI assistant that extracts key information from a raw issue report.
Given the following issue text, identify and list:

1. reported_issues: a concise list (bullet points or numbered) describing what’s wrong.
2. affected_components: which features or components are impacted.
3. severity: an inferred severity level (choose from Low, Medium, High, Critical).

Issue text:
\"\"\"
{issue_text}
\"\"\"

Respond in STRICTLY valid JSON with the following keys:
  - "reported_issues" (array of strings),
  - "affected_components" (array of strings),
  - "severity" (single string).

Example output format:
{{
  "reported_issues": [
    "Issue A ...",
    "Issue B ..."
  ],
  "affected_components": [
    "Component X",
    "Feature Y"
  ],
  "severity": "High"
}}
"""
    return template.format(issue_text=issue_text)


def call_llm_for_summary(prompt: str, llm: OpenAI) -> str:
    return llm(prompt)


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

    prompt = create_issue_summary_prompt(issue_text)
    llm = OpenAI(temperature=0)

    try:
        raw_response = call_llm_for_summary(prompt, llm)
    except Exception as e:
        return {"error": f"LLM call failed: {e}", "raw_response": ""}

    return parse_issue_summary_response(raw_response)
