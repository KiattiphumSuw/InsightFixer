from typing import Any
from langchain_openai import OpenAI
import json

# from langchain.tools import tool

from ..common.prompt import EXTRACT_ISSUE_PROMPT

# from langchain.prompts import PromptTemplate


# EXTRACT_ISSUE_PROMPT = PromptTemplate.from_template(
#     """
#     You are an AI assistant that extracts key information from a raw issue report.

#     Given the following issue text, extract the following fields:
#       1. "reported_issues": a list of concise descriptions (strings) of what’s wrong.
#       2. "affected_components": a list of which features or components are impacted.
#       3. "severity": an inferred severity level; one of "Low", "Medium", "High", or "Critical".

#     Issue Text:
#     {issue_text}

#     ⛔ Output Constraints:
#     - Your entire response must be exactly one valid JSON object.
#     - Do NOT include any explanation or comments outside the JSON.
#     - All field names must be enclosed in double quotes.
#     - Escape any internal quotes properly.
#     - If you include intermediate reasoning, place it under a top-level "reasoning" field.
#       Otherwise, you may omit "reasoning".

#     ✅ Expected JSON format:
#     {{
#       "reasoning": "<optional multi-line explanation of your thought process here>",
#       "response": {{
#         "reported_issues": [
#           "Issue A description",
#           "Issue B description"
#         ],
#         "affected_components": [
#           "Component X",
#           "Feature Y"
#         ],
#         "severity": "High"
#       }}
#     }}
#     """
# )


# @tool
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


if __name__ == "__main__":
    #     information = """Document Upload Stuck at 99%. When uploading large PDF documents (>50MB), the progress bar often gets stuck at 99% and never completes, even though the file appears to be uploaded successfully in the backend.
    # Steps to Reproduce:
    # 1. Navigate to the document upload section.
    # 2. Select a PDF file larger than 50MB.
    # 3. Observe the progress bar.
    # # """
    information = "Document Upload Stuck at 99%. When uploading large PDF documents (>50MB), the progress bar often gets stuck at 99% and never completes, even though the file appears to be uploaded successfully in the backend."
    result = issue_summary_tool(information)
    print(result)
