from langgraph.graph import END, StateGraph

from app.llm.provider import get_llm
from app.orchestrator.state import AgentState

llm = get_llm()


async def chat_node(state: AgentState) -> AgentState:
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("chat", chat_node)
    graph.set_entry_point("chat")
    graph.add_edge("chat", END)
    return graph.compile()


orchestrator = build_graph()
