from ai.graph.states import TaskState
from ai.graph.system_messages import system_messages_task_executer
from ai.graph.config import llm_groq_with_tools
from langchain_core.messages import HumanMessage


def research_executer(state: TaskState):
    messages = state.get("messages", [])

    # Initialize this worker's conversation only once
    if not messages:
        messages = [
            system_messages_task_executer,
            HumanMessage(content=state["task"]),
        ]

    response = llm_groq_with_tools.invoke(messages)

    updates = {"messages": [response]}

    # Only save the final answer, not intermediate tool-call requests
    if not response.tool_calls:
        updates["search_results"] = [response.content]

    return updates