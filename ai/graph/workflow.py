import ai.observability  # noqa: F401 - ensures LangGraph OTEL env vars and Logfire are ready
import logfire
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send
from ai.graph.states import ResearchState,TaskState
from ai.graph.nodes.research_planner import research_planner
from ai.graph.nodes.research_executer import research_executer
from ai.graph.subgraphs.research_worker import research_worker_graph
from rich import print


def dispatch_task(state: ResearchState):
    return [
        Send("research_worker", {"task": task})
        for task in state["research_plan"]
    ]


def run_research_worker(state: TaskState):
    result = research_worker_graph.invoke({
        "task": state["task"],
    })

    return {
        "search_results": result.get("search_results", []),
    }

# Build the research workflow graph
builder = StateGraph(ResearchState)

builder.add_node("research_planner", research_planner)
builder.add_node("research_worker", run_research_worker)

builder.add_edge(START, "research_planner")
builder.add_conditional_edges("research_planner", dispatch_task)
builder.add_edge("research_worker", END)
graph = builder.compile()

logfire.info("ResearchPilot StateGraph workflow compiled successfully")


def ask_ai(question: str) -> str:
    """Execute the ResearchPilot AI graph with the provided question."""
    with logfire.span("ask_ai: {question}", question=question):
        logfire.info("Invoking ResearchPilot graph", question=question)
        try:
            output = graph.invoke({
                "question": question,
                "messages": [],
            })
            result = output.get("search_results", [])
            logfire.info(
                "Graph execution completed successfully",
                question=question,
                report_length=len(result),
                tasks_executed=len(output.get("search_results", [])),
            )
            return result

        except Exception as e:
            logfire.exception("Error executing ResearchPilot graph: {error}", error=str(e), question=question)
            raise


if __name__ == "__main__":
    result = ask_ai("future of data engineering")
    print(result)
