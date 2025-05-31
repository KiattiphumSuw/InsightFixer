from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from src.tools.qdrant_search_tool import search_bug_reports
from src.tools.issue_summarizer import issue_summary_tool
import json

llm = ChatOpenAI(model="gpt-4", temperature=0)

internal_qa_tool = Tool(
    name="search bug reports",
    func=search_bug_reports,
    description="Searches internal bug reports by semantic meaning from user query."
)

issue_summary_chain_tool = Tool(
    name="IssueSummary",
    func=lambda text: json.dumps(issue_summary_tool(text)),
    description=(
        "Use this to summarize a raw issue report. Input: multi-line issue text. "
        "Output: JSON with keys 'reported_issues', "
        "'affected_components', and 'severity'."
    )
)

tools = [internal_qa_tool, issue_summary_chain_tool]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

def run_agent(query: str) -> str:
    return agent.run(query)
