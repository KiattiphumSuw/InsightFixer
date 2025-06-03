from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from ..common import SYSTEM_PROMPT
from ..tools import (answer_question_tool, issue_summary_tool,
                     search_bug_reports, search_user_feedbacks)


class InternalAgent:
    checkpointer = InMemorySaver()
    llm_model = "openai:gpt-4o-mini"
    system_prompt = SYSTEM_PROMPT
    tools = [search_bug_reports, search_user_feedbacks, issue_summary_tool, answer_question_tool]

    agent = create_react_agent(
            model=llm_model,
            tools=tools,
            prompt=system_prompt,
            debug=True,
            checkpointer=checkpointer
        )
    config = {"configurable": {"thread_id": "1"}}

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