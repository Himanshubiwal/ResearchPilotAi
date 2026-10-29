from ai.graph.states import ResearchState
from ai.graph.system_messages import system_messages_planner
from langchain_core.messages import HumanMessage
from ai.graph.config import llm_groq
from rich import print
import json,re 
import logfire






def research_planner(state: ResearchState):
    """ it will create a research plan for the query"""
    print("planner runns")
    plan_list = llm_groq.invoke([
        system_messages_planner,
        HumanMessage(content=state["question"])
    ])

    text = plan_list.content  # your string

    # 1. Remove the ```python ... ``` fences if present
    text = re.sub(r"^```(?:python|json)?\s*|\s*```$", "", text.strip())

    # 2. Parse it; strict=False allows line breaks inside the strings
    steps = json.loads(text, strict=False)

    # 3. Clean up the extra spaces left by the line breaks
    steps = [re.sub(r"\s+", " ", s).strip() for s in steps]

    print(steps)

    return {
        "research_plan": steps,
        "messages":[plan_list]
    }


