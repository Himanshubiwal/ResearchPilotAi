from sqlalchemy import exc
from ai.graph.states import ResearchState
from ai.graph.system_messages import system_messages_planner
from langchain_core.messages import HumanMessage
from ai.graph.config import llm_gemini
from rich import print
import json,re 
import logfire
import ast





def research_planner(state: ResearchState):
    try:
        with logfire.span("research_planner"):
            """ it will create a research plan for the query"""
            print("planner runns")
            with logfire.span("llm_groq called "):
                plan_list = llm_gemini.invoke([
                    system_messages_planner,
                    HumanMessage(content=state['question'])
                ])
                print(plan_list)
            steps = ast.literal_eval(plan_list.content[0]['text'])
            print(steps,type(steps))
            return {
                "research_plan": steps,
                "messages":[plan_list]
            }
    except Exception:
        logfire.exception("research_planner failed")


