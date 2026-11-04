from ai.graph.states import ResearchState
from ai.graph.system_messages import system_messages_planner
from langchain_core.messages import HumanMessage
from ai.graph.config import llm
from rich import print
import json
import re
import logfire


def research_planner(state: ResearchState):
    try:
        with logfire.span("research_planner"):
            """ it will create a research plan for the query"""
            with logfire.span("llm called for planning"):
                plan_list = llm.invoke([
                    system_messages_planner,
                    HumanMessage(content=state['question'])
                ])
                logfire.info("Planner LLM response received")

            # Strip markdown code fences if present
            raw = plan_list.content.strip()
            raw = re.sub(r"^```(?:python|json)?\s*\n?", "", raw)
            raw = re.sub(r"\n?```\s*$", "", raw)
            raw = raw.strip()

            try:
                steps = json.loads(raw)
            except json.JSONDecodeError:
                import ast
                steps = ast.literal_eval(raw)

            if not isinstance(steps, list) or not steps:
                raise ValueError(f"Planner returned invalid plan: {raw[:200]}")

            return {
                "research_plan": steps,
                "messages": [plan_list]
            }
    except Exception:
        logfire.exception("research_planner failed")
        raise
