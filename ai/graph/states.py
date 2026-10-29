from ast import operator
from filetype.types import document
from typing import TypedDict, Annotated, List, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from operator import add

class ResearchState(TypedDict, total=False):
    # 1. User input
    question: str
    messages: Annotated[List[AnyMessage], add_messages]

    # 2. Research planning
    research_plan: list[str]
    current_step: int
    search_results: Annotated[List[str],add]

    # 4. Evidence and analysis
    gathered_evidence: list[dict]
    findings: list[str]

    # 5. Verification
    verification_results: list[dict]

    # 6. Final output
    report: str
    citations: list[dict]

    # 7. Execution control
    retry_count: int
    errors: list[str]


class TaskState(TypedDict, total=False):
    task: str



class TaskState(TypedDict, total=False):
    task: str
    messages: Annotated[list[AnyMessage], add_messages]
    search_results: Annotated[list[str], add]