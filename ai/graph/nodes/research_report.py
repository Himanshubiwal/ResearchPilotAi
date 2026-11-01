from urllib3.exceptions import ResponseNotChunked
from ai.graph.states import ResearchState
from ai.graph.system_messages import REPORT_WRITER_SYSTEM_PROMPT
from ai.graph.config import llm
from langchain_core.messages import HumanMessage
import logfire


def research_report(state:ResearchState):
    try:
        with logfire.span("writing final report"):
            human_message = HumanMessage(
            content=f"""
            Original Research Question:
            {state["question"]}

            Research Results:
            {state["search_results"]}

            Gathered Evidence:
            {state["gathered_evidence"]}

            Write the final research report using the provided information.
            """
        )
            with logfire.span("llm is writing final report"):
                response = llm.invoke([REPORT_WRITER_SYSTEM_PROMPT,human_message])


            return {
                "report":response.content
            }
    except Exception:
        logfire.exception("report writer faild")
        raise