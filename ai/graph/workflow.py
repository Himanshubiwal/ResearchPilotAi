from litellm.proxy.pass_through_endpoints.llm_provider_handlers.transcribe_passthrough_logging_handler import price_transcription_job
import ai.observability  # noqa: F401 - ensures LangGraph OTEL env vars and Logfire are ready
import logfire
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send
from ai.graph.states import ResearchState,TaskState
from ai.graph.nodes.research_planner import research_planner
from ai.graph.nodes.research_executer import research_executer
from ai.graph.subgraphs.research_worker import research_worker_graph
from rich import print
from ai.graph.nodes.results_verify import results_verify
from ai.graph.nodes.research_report import research_report






def dispatch_task(state: ResearchState):

    feedback= {}
    if state.get("verification_results",[]):
        feedback=state.get("verification_results",[])[-1]
    return [
        Send("research_worker", {"task": task,
        "search_results":state.get('search_results',[]),
        "evidence":state.get('gathered_evidence',[]),
        "feedback":feedback
        })
        for task in state["research_plan"]
    ]


def run_research_worker(state: TaskState):
    result = research_worker_graph.invoke({
        "task": state["task"],
        "search_results":state['search_results'],
        "evidence":state['evidence'],
        "feedback":state["feedback"]
    })

    with logfire.span("saperating results and evidences in n*n complexity"):
        search_results=[]
        gathered_evidence=[]
        print(result["search_results"])
        for r in result["search_results"]:
            search_results.append(r["content"])
            for e in r['evidence']:
                gathered_evidence.append(e)

    return {
        "search_results": search_results,
        "gathered_evidence":gathered_evidence,
    }

#     status: Literal["passed", "failed", "partial"]


def decide_path(state:ResearchState):
    verification_result =state["verification_results"]
    if verification_result[-1]["status"]=="passed":
        return "research_report"
    else :
        return "research_planner"



# Build the research workflow graph
builder = StateGraph(ResearchState)

builder.add_node("research_planner", research_planner)
builder.add_node("research_worker", run_research_worker)
builder.add_node("results_verify",results_verify)
builder.add_node("research_report",research_report)

builder.add_edge(START, "research_planner")
builder.add_conditional_edges("research_planner", dispatch_task)
builder.add_edge("research_worker", "results_verify")
builder.add_conditional_edges("results_verify",
                decide_path,
                {
                    "research_planner":"research_planner",
                    "research_report":"research_report"
                }
                )
builder.add_edge("research_report",END)
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
    result = ask_ai("future of data engineering")
    print(result)
