from typing import TypedDict, Annotated, List, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage


class ResearchState(TypedDict, total=False):
    # 1. User input
    question: str
    messages: Annotated[List[AnyMessage], add_messages]

    # 2. Research planning
    research_plan: list[str]
    current_step: int

    # 3. Web research
    search_queries: list[str]
    search_results: list[dict]

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
