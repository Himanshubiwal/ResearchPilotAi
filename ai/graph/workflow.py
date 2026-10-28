import ai.observability  # noqa: F401 - ensures LangGraph OTEL env vars and Logfire are ready
import logfire
from ai.graph.states import ResearchState
from ai.graph.nodes import add_human_message, get_response
from langgraph.graph import START, END, StateGraph
from langchain_core.messages import SystemMessage








# Build the research workflow graph
builder = StateGraph(ResearchState)

builder.add_node("add_human_message", add_human_message)
builder.add_node("get_response", get_response)

builder.add_edge(START, "add_human_message")
builder.add_edge("add_human_message", "get_response")
builder.add_edge("get_response", END)
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
            final_message = output["messages"][-1]
            response_content = getattr(final_message, "content", str(final_message))
            logfire.info(
                "Graph execution completed successfully",
                question=question,
                response_length=len(str(response_content)),
                total_messages=len(output.get("messages", [])),
            )
            return response_content

        except Exception as e:
            logfire.exception("Error executing ResearchPilot graph: {error}", error=str(e), question=question)
            raise