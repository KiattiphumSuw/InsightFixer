import re

from langchain.embeddings import OpenAIEmbeddings
from qdrant_client import QdrantClient, models

import json
from typing import Any, Optional
from langchain_community.llms import OpenAI
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

BUG_COLLECTION_NAME = "internal-bug-reports"

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


def search_bug_reports_semantic(query: str) -> Optional[dict[str, dict[str, Any]]]:
    """
    Perform a semantic search in Qdrant for the given query string.
    Returns a dict mapping bug_number to its metadata+content, or None if no hits.
    """
    embeddings = OpenAIEmbeddings()
    client = QdrantClient(host="localhost", port=6333)
    vector = embeddings.embed_query(query)

    hits = client.search(
        collection_name=BUG_COLLECTION_NAME,
        query_vector=vector,
        limit=3,
        with_payload=True
    )

    if not hits:
        return None

    results: dict[str, dict[str, Any]] = {}
    for hit in hits:
        payload = hit.payload or {}
        metadata = payload.get("metadata", {})
        # Attach the actual page_content under "content"
        metadata["content"] = payload.get("page_content", "")
        bug_number = metadata.get("bug_number", f"unknown_{hit.id}")
        metadata.pop("bug_number", None)
        results[str(bug_number)] = metadata

    return results


def search_bug_reports_by_number(bug_number: int) -> Optional[dict[str, Any]]:
    """
    Retrieve a single bug report from Qdrant by matching its metadata.bug_number.
    Returns a dict with that bug's metadata+content, or None if not found.
    """
    client = QdrantClient(host="localhost", port=6333)
    hits, _ = client.scroll(
        collection_name=BUG_COLLECTION_NAME,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.bug_number",
                    match=models.MatchValue(value=str(bug_number)),
                ),
            ]
        ),
    )
    if not hits:
        return None
    payload = hits[0].payload or {}
    metadata = payload.get("metadata", {})
    metadata["content"] = payload.get("page_content", "")
    metadata.pop("bug_number", None)
    return metadata


def issue_summary_by_search_tool(user_query: str) -> dict[str, Any]:
    """
    1. If `user_query` explicitly asks for "bug" or "issue" followed by a number (e.g., "Summarize issue number 5"),
       fetch that bug by metadata.
    2. Otherwise, perform a semantic search over all bug reports.
    3. If any hits are found, aggregate and send to LLM for summarization.
    4. If no hits, return an error indicating no relevant bug found.

    Returns a dict with either:
      - {"bug_number": 5, "parsed_summary": {...}, "raw_response": "<LLM JSON>"}  (single-bug case)
      - {"bug_summaries": {<bug_number>: metadata, ...}, "raw_response": "<LLM JSON>"}  (multi-bug case)
      - {"error": "..."}  (no hits or other failure)
    """
    if not user_query or not user_query.strip():
        return {"error": "No query provided."}

    query = user_query.strip()

    # 1) Check for "bug" or "issue" followed by a number (case-insensitive, allows "summarize issue number 5" etc.)
    m = re.search(r"\b(?:bug|issue)\s*(?:number\s*)?#?(\d+)\b", query, re.IGNORECASE)
    if m:
        bug_num = int(m.group(1))
        single_bug = search_bug_reports_by_number(bug_num)

        if not single_bug:
            return {"error": f"Bug number {bug_num} not found."}

        # Build a raw-issue text for the LLM to summarize
        title = single_bug.get("title", f"Bug #{bug_num}")
        description = single_bug.get("content", "")
        raw_issue_text = f"Title: {title}\nDescription: {description}"

        prompt = create_issue_summary_prompt(raw_issue_text)
        llm = OpenAI(temperature=0)
        try:
            raw_response = call_llm_for_summary(prompt, llm)
        except Exception as e:
            return {"error": f"LLM call failed for bug #{bug_num}: {e}"}

        parsed = parse_issue_summary_response(raw_response)
        return {
            "bug_number": bug_num,
            "parsed_summary": parsed,
            "raw_response": raw_response
        }
    # 2) If no explicit bug/issue number, run a semantic search
    semantic_hits = search_bug_reports_semantic(query)
    if not semantic_hits:
        return {"error": "No relevant bug reports found."}

    # 3) Aggregate top hits' content for summarization
    combined_content = ""
    for bug_num, metadata in semantic_hits.items():
        title = metadata.get("title", f"Bug #{bug_num}")
        description = metadata.get("content", "")
        combined_content += f"Bug #{bug_num} - {title}\n{description}\n\n"

    summary_prompt = (
        "You are an AI assistant. Given the following bug reports, "
        "provide a concise summary of the collective issues, affected components, "
        "and suggest an overall severity if applicable.\n\n"
        f"{combined_content}\n"
        "Respond in valid JSON with keys:\n"
        "  - \"aggregated_summary\": a short paragraph summarizing the issues,\n"
        "  - \"key_components\": list of components impacted,\n"
        "  - \"overall_severity\": one of [\"Low\", \"Medium\", \"High\", \"Critical\"]."
    )

    llm = OpenAI(temperature=0)
    try:
        raw_response = llm(summary_prompt)
    except Exception as e:
        return {"error": f"LLM call failed during aggregated summary: {e}"}

    return {
        "bug_summaries": semantic_hits,
        "raw_response": raw_response
    }


if __name__ == "__main__":
    result = issue_summary_by_search_tool("issue number 5")
    # result = search_bug_reports_by_number(5)
    print(result)