from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from rich import print



llm = ChatOllama(
    model="hf.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-4GB:Q4_K_M",
    temperature=0.7,
    num_ctx=2048,  # keep modest on 8 GB RAM
)

response = llm.invoke([
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Explain recursion ."),
])
print(response)