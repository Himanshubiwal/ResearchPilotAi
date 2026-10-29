import os
from dotenv import load_dotenv
import logfire
import ai.observability  # noqa: F401
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from ai.graph.tools.doc_retrieval import doc_retrieval
from ai.graph.tools.web_search import web_search



load_dotenv()

Google_api_key = os.getenv("GEMINI_API_KEY")
Groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGoogleGenerativeAI(
    api_key=Google_api_key,
    model="gemini-3-pro",
    temperature=0.1,
    max_tokens=2500,
)
tools = [web_search,doc_retrieval]


llm_groq = ChatGroq(
    api_key=Groq_api_key,
    model="openai/gpt-oss-120b",
    temperature=0.1,
    max_tokens=2000,
)

llm_groq_with_tools = llm_groq.bind_tools(tools)
logfire.info(
    "LLM clients initialized",
    gemini_model="gemini-3-pro",
    groq_model="openai/gpt-oss-120b",
    gemini_key_set=bool(Google_api_key),
    groq_key_set=bool(Groq_api_key),
)