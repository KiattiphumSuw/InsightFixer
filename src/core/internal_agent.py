from langgraph.prebuilt import create_react_agent
from src.tools.qdrant_search_tool import search_bug_reports, search_user_feedbacks
from src.tools.issue_summarizer import issue_summary_tool
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
llm_model = "openai:gpt-4o-mini"
system_prompt = (
        "You are an internal AI assistant for the product and engineering team. "
        "When a user asks about bugs or feedback, first call the `search_bug_reports` tool "
        "to retrieve relevant raw issue text. Then, if summarization is requested, "
        "call `issue_summary_tool` on the retrieved text to extract "
        "reported issues, affected components, and severity."
    )
tools = [search_bug_reports, search_user_feedbacks, issue_summary_tool]
agent = create_react_agent(
        model=llm_model,
        tools=[search_bug_reports, issue_summary_tool],
        prompt=system_prompt,
        debug=True,
        checkpointer=checkpointer
    )
config = {"configurable": {"thread_id": "1"}}

def run_agent(query: str) -> str:
    inputs = {
        "messages": [
            {
                "role": "user",
                "content": f"{query}"
            }
        ]
    }
    response = agent.invoke(inputs, config)
    final_message = response["messages"][-1]
    result = final_message.content
    return result