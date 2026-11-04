from langchain_core.messages import AIMessage
import logfire
from ai.graph.states import TaskState
from ai.graph.system_messages import system_messages_task_executer
from ai.graph.config import llm_with_tool, structured_llm
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage


def research_executer(state: TaskState):
    try:
        with logfire.span("research_executor"):
            messages = state.get("messages", [])
            is_first_call = not messages

            # Build the initial prompt on first invocation
            if is_first_call:
                messages = [system_messages_task_executer]

                if state.get('feedback'):
                    messages.append(HumanMessage(
                        content=f"""
                        Research Task:
                        {state["task"]}
                        Previous Research Result:
                        {state.get("search_results", [])}
                        Previous Evidence:
                        {state.get("evidence", [])}
                        Verification Feedback:
                        {state.get("feedback", {})}
                        Improve the research using the verification feedback.
                        Address unsupported claims, missing evidence, and identified issues.
                        Gather additional evidence if necessary.
                        Return an updated result, gathered evidence, and findings.
                        """
                    ))
                else:
                    messages.append(HumanMessage(
                        content=f"Research Task:\n{state['task']}"
                    ))

            with logfire.span("llm tool call"):
                response = llm_with_tool.invoke(messages)

            # Build state updates
            if is_first_call:
                updates = {"messages": messages + [response]}
            else:
                updates = {"messages": [response]}

            # Only save the final answer, not intermediate tool-call requests
            if not response.tool_calls:
                with logfire.span("save final answer"):
                    structured_response = structured_llm.invoke(
                        [
                            SystemMessage(
                                content=(
                                    "Generate a research result using the conversation "
                                    "and tool results. Include supporting evidence."
                                )
                            ),
                            HumanMessage(
                                content=response.content
                            )
                        ]
                    )
                    results = structured_response.model_dump()
                    updates["search_results"] = [results]

            return updates
    except Exception:
        logfire.exception("Research_executor failed")
        raise
