import logfire
from langchain_tavily import TavilySearch,TavilyResearch
import os
from dotenv import load_dotenv
from rich import print


load_dotenv()


tavily_api_key = os.getenv("TAVILY_API_KEY")

if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY is not configured")
try:
    with logfire.span("tavily tool call is running"):
        web_search= TavilySearch(
            max_results = 2 ,
            tavily_api_key= tavily_api_key
        )
        logfire.info("tavily call successfull")

except Exception:
    logfire.exception("Web Search tool failed")
    raise




