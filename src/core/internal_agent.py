from langgraph.prebuilt import create_react_agent
from src.tools.qdrant_search_tool import search_bug_reports, search_user_feedbacks
from src.tools.issue_summarizer import issue_summary_tool, issue_summary_by_search_tool
from langgraph.checkpoint.memory import InMemorySaver

class InternalAgent:
    checkpointer = InMemorySaver()
    llm_model = "openai:gpt-4o-mini"
    system_prompt = (
        "You are an internal AI assistant for the product and engineering team. "
        "When the user asks about bugs or feedback:\n"
        "  1. If the query explicitly references a bug number (e.g., “Summarize issue number 5”), "
        "invoke `issue_summary_by_search_tool` with the user’s query to fetch and summarize that specific bug.\n"
        "  2. Otherwise:\n"
        "     • If it’s a bug-related question, invoke `search_bug_reports` to retrieve raw issue text.\n"
        "     • If it’s a feedback-related question, invoke `search_user_feedbacks` to retrieve raw feedback text.\n"
        "     • If the user requests a summary of any retrieved content, always invoke `issue_summary_tool` on those results to extract and include:\n"
        "       – reported_issues\n"
        "       – affected_components\n"
        "       – severity\n"
        "Use the structured output returned by these tools to build your response."
    )
    tools = [search_bug_reports, search_user_feedbacks, issue_summary_tool, issue_summary_by_search_tool]

    agent = create_react_agent(
            model=llm_model,
            tools=tools,
            prompt=system_prompt,
            debug=True,
            checkpointer=checkpointer
        )
    config = {"configurable": {"thread_id": "1"}}
    def __init__(self):
        pass

    def ask_agent(self, query: str) -> str:
        inputs = {
            "messages": [
                {
                    "role": "user",
                    "content": f"{query}"
                }
            ]
        }
        response = self.agent.invoke(inputs, self.config)
        final_message = response["messages"][-1]
        result = final_message.content
        return result