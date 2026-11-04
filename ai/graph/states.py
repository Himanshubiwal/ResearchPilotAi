from typing import TypedDict, Annotated, List
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
    gathered_evidence:Annotated[list[dict],add]

    # 5. Verification
    verification_results:Annotated[list[dict],add]
    feedback:Annotated[list[dict],add]

    # 6. Final output
    report: str
    citations: list[dict]

    # 7. Execution control
    retry_count: int
    errors: list[str]



class TaskState(TypedDict, total=False):
    task: str
    messages: Annotated[List[AnyMessage], add_messages]
    search_results: Annotated[List[dict], add]
    feedback:dict
    evidence:list[dict]


