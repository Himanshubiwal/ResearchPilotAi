from langchain_core.messages import AIMessage
import logfire
from ai.graph.states import TaskState
from ai.graph.system_messages import system_messages_task_executer
from ai.graph.config import llm_with_tool,structured_llm
from langchain_core.messages import HumanMessage,SystemMessage,ToolMessage
from rich import print


def research_executer(state: TaskState):
    try:
        with logfire.span("research_executor"):
            messages = state.get("messages", [])
            flag = False
            # Initialize this worker's conversation only once


            human_message = HumanMessage(
                content=f"""
                Research Task:
                {state["task"]}
                Previous Research Result:
                {state["search_results"]}
                Previous Evidence:
                {state["evidence"]}
                Verification Feedback:
                {state["feedback"]}
                Improve the research using the verification feedback.
                Address unsupported claims, missing evidence, and identified issues.
                Gather additional evidence if necessary.
                Return an updated result, gathered evidence, and findings.
                """
            )
            if not messages:
                messages = [
                    system_messages_task_executer,
                    
                ]
                if state['feedback']:
                    messages.append(human_message)
                else:
                    messages.append(HumanMessage(
                        content=f"Research Task:\n{state['task']}"
                    ))
                flag=True
            with logfire.span("llm tool call"):

                response = llm_with_tool.invoke(messages)
            updates = {"messages": [response]}
            if flag:
                updates={"messages":messages+[response]}
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
                    
                    print(state["messages"])
            return updates
    except Exception: 
        logfire.exception("Research_executor failed")
        raise