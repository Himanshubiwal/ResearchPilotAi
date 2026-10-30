import logfire
from ai.graph.states import TaskState
from ai.graph.system_messages import system_messages_task_executer
from ai.graph.config import structured_output_llm_gemini,llm_groq_with_tools
from langchain_core.messages import HumanMessage


def research_executer(state: TaskState):
    try:
        with logfire.span("research_executor"):
            messages = state.get("messages", [])

            # Initialize this worker's conversation only once
            if not messages:
                messages = [
                    system_messages_task_executer,
                    HumanMessage(content=state["task"]),
                ]
            with logfire.span("llm tool call"):
                response = llm_groq_with_tools.invoke(messages)
            updates = {"messages": [response]}

            # Only save the final answer, not intermediate tool-call requests
            if not response.tool_calls:
                with logfire.span("save final answer"):
                    structured_response = structured_output_llm_gemini.invoke([HumanMessage(content=f"{response.content}")])
                    results = structured_response.model_dump()
                    updates["search_results"] = [results]

            return updates
    except Exception: 
        logfire.exception("Research_executor failed")
        raise