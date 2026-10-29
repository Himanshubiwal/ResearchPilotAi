from ai.retrieval.retriever import retrieve_chunks
from langchain_core.tools import tool



@tool
def doc_retrieval(query: str):
    """ Use this tool when the task requires information from user-provided documents
or previously indexed content. Do not use it to find the latest external
information or general web sources"""
    return retrieve_chunks(query) 
