import ai.observability  # noqa: F401 - ensures LangGraph OTEL env vars and Logfire are ready
import logfire
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send
from ai.graph.states import ResearchState, TaskState
from ai.graph.nodes.research_planner import research_planner
from ai.graph.nodes.research_executer import research_executer
from ai.graph.subgraphs.research_worker import research_worker_graph
from rich import print
from ai.graph.nodes.results_verify import results_verify
from ai.graph.nodes.research_report import research_report


MAX_RETRIES = 3


def dispatch_task(state: ResearchState):

    feedback = {}
    if state.get("verification_results", []):
        feedback = state.get("verification_results", [])[-1]

    research_plan = state.get("research_plan", [])
    if not research_plan:
        logfire.error("dispatch_task: research_plan is empty or missing")
        return []

    return [
        Send("research_worker", {
            "task": task,
            "search_results": state.get('search_results', []),
            "evidence": state.get('gathered_evidence', []),
            "feedback": feedback
        })
        for task in research_plan
    ]


def run_research_worker(state: TaskState):
    result = research_worker_graph.invoke({
        "task": state["task"],
        "search_results": state.get('search_results', []),
        "evidence": state.get('evidence', []),
        "feedback": state.get("feedback", {})
    })

    with logfire.span("separating results and evidence"):
        search_results = []
        gathered_evidence = []
        for r in result.get("search_results", []):
            if isinstance(r, dict):
                search_results.append(r.get("content", ""))
                for e in r.get('evidence', []):
                    gathered_evidence.append(e)
            elif isinstance(r, str):
                search_results.append(r)

    return {
        "search_results": search_results,
        "gathered_evidence": gathered_evidence,
    }


def decide_path(state: ResearchState):
    # Enforce retry limit to prevent infinite loops
    if state.get("retry_count", 0) >= MAX_RETRIES:
        logfire.warning(
            "Max retries reached, proceeding to report",
            retry_count=state.get("retry_count", 0),
        )
        return "research_report"

    verification_results = state.get("verification_results", [])
    if not verification_results:
        return "research_report"

    if verification_results[-1].get("status") == "passed":
        return "research_report"
    else:
        return "research_planner"


# Build the research workflow graph
builder = StateGraph(ResearchState)

builder.add_node("research_planner", research_planner)
builder.add_node("research_worker", run_research_worker)
builder.add_node("results_verify", results_verify)
builder.add_node("research_report", research_report)

builder.add_edge(START, "research_planner")
builder.add_conditional_edges("research_planner", dispatch_task)
builder.add_edge("research_worker", "results_verify")
builder.add_conditional_edges("results_verify",
                decide_path,
                {
                    "research_planner": "research_planner",
                    "research_report": "research_report"
                }
                )
builder.add_edge("research_report", END)
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
            
            result = output.get("report", "")
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
    result = ask_ai("Based on our uploaded psycholinguistics notes, explain the pre-lexical analysis and contact/activation stages in spoken word recognition.")
    print(result)
