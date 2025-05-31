from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from src.tools.qdrant_search_tool import search_bug_reports

llm = ChatOpenAI(model="gpt-4", temperature=0)

tools = [
    Tool.from_function(
        func=search_bug_reports,
        name="search bug reports",
        description="Searches internal bug reports by semantic meaning from user query."
    )
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

def run_agent(query: str) -> str:
    return agent.run(query)
