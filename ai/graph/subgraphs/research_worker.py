from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode, tools_condition
import logfire
from ai.graph.states import TaskState
from ai.graph.config import tools
from ai.graph.nodes.research_executer import research_executer
from langchain_core.callbacks import BaseCallbackHandler

worker_builder = StateGraph(TaskState)
class ToolCounter(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.by_tool = {}

    def on_tool_start(self, serialized, input_str, **kwargs):
        name = (serialized or {}).get("name") or kwargs.get("name") or "unknown"
        self.count += 1
        self.by_tool[name] = self.by_tool.get(name, 0) + 1
        logfire.info("ToolCounter: tool started", tool_name=name, count=self.count)



try:
    with logfire.span("building research_worker_graph"):
        worker_builder.add_node(
            "research_executer",
            research_executer,
        )

        worker_builder.add_node(
            "tool_node",
            ToolNode(tools),
        )
        worker_builder.add_edge(START, "research_executer")
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
        logfire.info("research_worker_graph compiled successfully")
except Exception:
    logfire.exception("research_worker_graph building failed")
    raise
