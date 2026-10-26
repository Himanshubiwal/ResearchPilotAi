
from langgraph.constants import END
from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import os
from langgraph.graph import START,START,StateGraph 
from dotenv import load_dotenv
from rich import print
# Load .env file
load_dotenv()

Google_api_key = os.getenv("GEMINI_API_KEY")
Groq_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGoogleGenerativeAI(
    api_key=Google_api_key,
    model="gemini-3.8-flash",
    temperature = 0.1,
    max_tokens = 2500 
)

llm_groq= ChatGroq(
    api_key=Groq_api_key,
    model="openai/gpt-oss-120b",
    temperature=0.1,
    max_tokens=2000
)
class ResearchState(TypedDict): 
    # 1. User input
    question: str

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
    temporary_results:str
    


def results(state:ResearchState):

    results = llm.invoke(state['question'])

    return {"temporary_results": results.content}




builder=StateGraph(ResearchState)
builder.add_node("results",results)

builder.add_edge(START,"results")
builder.add_edge("results", END)
graph = builder.compile()





print("message daal dalle:")

while True :
    query=input("your query>>")
    output= graph.invoke(
    {
        "question":query
    }
    )
    print(output['temporary_results'][0]['text'])