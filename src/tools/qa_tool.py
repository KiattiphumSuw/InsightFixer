from typing import Any
from langchain_openai import OpenAI
import json

# from langchain.tools import tool

from ..common.prompt import ANSWER_QUESTION_PROMPT

# from langchain.prompts import PromptTemplate

# ANSWER_QUESTION_PROMPT = PromptTemplate.from_template(
#     """
#     You are a developer-focused AI assistant. Use the information below to answer the question concisely and thoughtfully.

#     Information:
#     {information}

#     Question:
#     {question}

#     Instructions:
#     1. Analyze the question and provided information. If the answer is not directly stated, reason through the necessary steps.
#     2. If reasoning is required, embed all intermediate steps (Thought, Action, Observation) inside the "reasoning" field as a multi-line string.

#     3. Then, output ONLY a valid JSON object using the exact format below:
#     ```json
#     {{
#       "reasoning": "<multi-line explanation including thoughts, actions, and observations if needed>",
#       "response": "<concise answer to the question>"
#     }}
#     ```
#     ✱ Output Constraints:
#     - Output must be strictly valid JSON (double-quoted keys and values, properly escaped content).
#     - Do NOT output anything outside the JSON block.
#     - Place all reasoning (including Thought/Action/Observation if applicable) inside the "reasoning" field.
#     - Do not output Thought/Action/Observation outside of the JSON.
#     """
# )


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
        # cleaned_response = raw_response.replace("\n", "\\n").replace("\r", "\\r")

        parsed = json.loads(raw_response)

        return parsed

    except Exception as e:
        return {"error": e, "raw_response": raw_response}


# if __name__ == "__main__":
#     question = "What about bug Upload Stuck at 99%"
#     information = """Bug #1
# Title: Document Upload Stuck at 99%
# Description: When uploading large PDF documents (>50MB), the progress bar often gets stuck at 99% and never completes, even though the file appears to be uploaded successfully in the backend.
# Steps to Reproduce:
# 1. Navigate to the document upload section.
# 2. Select a PDF file larger than 50MB.
# 3. Observe the progress bar.
# Environment: Web (Chrome 123.x), Backend v1.0.5
# Severity: Medium
# Proposed Fix: Investigate potential race condition or finalization issue in the upload progress tracking.
#     """
#     a = answer_question_tool(question, information)
#     print(a)

#     raw_response = """

# {
#   "reasoning": "Thought: The bug is related to document upload getting stuck at 99%.\nAction: Analyze the provided information and steps to reproduce the bug.\nObservation: The bug occurs when uploading large PDF documents (>50MB) and the progress bar gets stuck at 99% even though the file appears to be uploaded successfully in the backend. The bug is reproducible in the web environment (Chrome 123.x) and backend v1.0.5. The severity of the bug is medium and the proposed fix is to investigate potential race condition or finalization issue in the upload progress tracking.",
#   "response": "The bug is related to document upload getting stuck at 99% when uploading large PDF documents (>50MB) in the web environment (Chrome 123.x) and backend v1.0.5. The proposed fix is to investigate potential race condition or finalization issue in the upload progress tracking."
# }
# """
# cleaned_response = raw_response.replace("\n", "\\n").replace("\r", "\\r")
# parsed = json.loads(raw_response)
# print(parsed)
