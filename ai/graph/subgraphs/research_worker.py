from langgraph.graph import StateGraph, END,START
from langgraph.prebuilt import ToolNode, tools_condition

from ai.graph.states import TaskState
from ai.graph.config import tools
from ai.graph.nodes.research_executer import research_executer


worker_builder = StateGraph(TaskState)

worker_builder.add_node(
    "research_executer",
    research_executer,
)

worker_builder.add_node(
    "tool_node",
    ToolNode(tools),
)
worker_builder.add_edge(START,"research_executer")
worker_builder.add_conditional_edges(
    "research_executer",
    tools_condition,
    {
        "tools": "tool_node",
        "__end__": END,
    },
)

worker_builder.add_edge(
    "tool_node",
    "research_executer",
)

research_worker_graph = worker_builder.compile()