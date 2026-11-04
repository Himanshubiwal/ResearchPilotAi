import os
from dotenv import load_dotenv
import logfire
import ai.observability  # noqa: F401
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from ai.graph.tools.doc_retrieval import doc_retrieval
from ai.graph.tools.web_search import web_search
from ai.graph.models.structured_output import TaskResults,VerificationResult
from langchain_openrouter import ChatOpenRouter
from langchain_openai import ChatOpenAI
from langchain_litellm import ChatLiteLLMRouter
from litellm import Router

load_dotenv()


Google_api_key = os.getenv("GEMINI_API_KEY")
Groq_api_key = os.getenv("GROQ_API_KEY")
Openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if not Google_api_key:
    raise ValueError("google api key is not configured")

if not Groq_api_key:
    raise ValueError("Groq api key is not configured")

if not Openrouter_api_key:
    raise ValueError("Openrouter api key is not configured")


# llm_gemini = ChatGoogleGenerativeAI(
#     api_key=Google_api_key,
#     model="gemini-3.5-flash-lite",
#     temperature=0.1,
#     max_tokens=2500,
# )
tools = [web_search,doc_retrieval]


# llm_groq = ChatGroq(
#     api_key=Groq_api_key,
#     model="openai/gpt-oss-120b",
#     temperature=0.1,
#     max_tokens=2000,
# )


# llm_openrouter=ChatOpenRouter(
#     api_key=Openrouter_api_key,
#     model="nvidia/nemotron-3-ultra-550b-a55b:free",
#     temperature=0,
#     max_retries=2,
# )

# llm_groq_with_tools = llm_groq.bind_tools(tools
# ,parallel_tool_calls=False)
# logfire.info(
#     "LLM clients initialized",
#     gemini_model="gemini-3-pro",
#     groq_model="openai/gpt-oss-120b",
#     gemini_key_set=bool(Google_api_key),
#     groq_key_set=bool(Groq_api_key),
# )
# llm_gemini_with_tools =llm_gemini.bind_tools(tools)

# structured_output_llm_gemini = llm_gemini.with_structured_output(TaskResults)
# structured_output_llm_groq = llm_groq.with_structured_output(TaskResults,
#     method="json_schema",
#     strict=True
# )

model_list = [
    {
        "model_name": "researchpilot",
        "litellm_params": {
            "model": "gemini/gemini-3.5-flash-lite",
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



structured_llm = llm.with_structured_output(TaskResults)
llm_with_tool = llm.bind_tools(tools)

structured_llm_verify = llm.with_structured_output(VerificationResult)


