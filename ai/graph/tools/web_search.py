from langchain_tavily import TavilySearch,TavilyResearch
import os
from dotenv import load_dotenv
from rich import print


load_dotenv()


tavil_api_key = os.getenv("TAVILY_API_KEY")
web_search= TavilySearch(
    max_result = 2 ,
    tavil_api_key= tavil_api_key
)

# web_research = TavilyResearch(

# )

results = web_search.invoke("what is weather today")

