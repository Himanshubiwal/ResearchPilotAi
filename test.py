from pydantic_core.core_schema import lax_or_strict_schema
from langchain_litellm import ChatLiteLLMRouter
from litellm import Router
import os 
from dotenv import load_dotenv
from langchain.messages import HumanMessage
load_dotenv()
from rich import print


Google_api_key = os.getenv("GEMINI_API_KEY")
Groq_api_key = os.getenv("GROQ_API_KEY")
Openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
model_list = [
    {
        "model_name": "researchpilot",
        "litellm_params": {
            "model": "gemini/gemini-3.df5-flash-lite",
            "api_key": Google_api_key,
        },
    },
    {
        "model_name": "researchpilot-fallback",
        "litellm_params": {
            "model": "groq/openai/gpt-oss-120b",
            "api_key": Groq_api_key,
        },
    },
]
litellm_router = Router(model_list=model_list,
    fallbacks=[
        {"researchpilot": ["researchpilot-fallback"]}
    ],)
llm = ChatLiteLLMRouter(router=litellm_router, model_name="researchpilot", temperature=0.1)






response = llm.invoke([HumanMessage(
    content="tell me about rag in 5 lines"
)])


print(response)


