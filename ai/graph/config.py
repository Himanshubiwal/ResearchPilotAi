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
from langchain_core.rate_limiters import InMemoryRateLimiter



load_dotenv()


Google_api_key_1 = os.getenv("GEMINI_API_KEY_1")
Google_api_key_2 = os.getenv("GEMINI_API_KEY_2")
Groq_api_key = os.getenv("GROQ_API_KEY")
Openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if not Google_api_key_1:
    raise ValueError("google api key is not configured")
if not Google_api_key_2:
    raise ValueError("google api key is not configured")

if not Groq_api_key:
    raise ValueError("Groq api key is not configured")

if not Openrouter_api_key:
    raise ValueError("Openrouter api key is not configured")



tools = [web_search,doc_retrieval]

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.3,
    check_every_n_seconds=0.1,
    max_bucket_size=1,
)


model_list = [
    {
            "model_name": "local",
            "litellm_params": {
                "model": "ollama_chat/hf.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-4GB:Q4_K_M",
                "api_base": "http://localhost:11434",
            },
        },
    {
        "model_name": "researchpilot",
        "litellm_params": {
            "model": "gemini/gemini-3.5-flash-lite",
            "api_key": Google_api_key_2,
            "rpm":12
        },
    },
    {
        "model_name": "researchpilot",
        "litellm_params": {
            "model": "gemini/gemini-3.5-flash-lite",
            "api_key": Google_api_key_1,
            "rpm":12
        },
    },

    {
        "model_name": "researchpilot-fallback",
        "litellm_params": {
            "model": "groq/openai/gpt-oss-120b",
            "api_key": Groq_api_key,
            "rpm":12
        },
    },
]


litellm_router = Router(
    model_list=model_list,
    routing_strategy="usage-based-routing-v2",
    fallbacks=[{"researchpilot": ["researchpilot-fallback"]}],
    num_retries=2,
    cooldown_time=10,
)

llm = ChatLiteLLMRouter(router=litellm_router, model_name="researchpilot", rate_limiter=rate_limiter)
llm_local = ChatLiteLLMRouter(router=litellm_router,model_name="local")


structured_llm = llm.with_structured_output(TaskResults)
llm_with_tool = llm.bind_tools(tools)

structured_llm_verify = llm.with_structured_output(VerificationResult)


