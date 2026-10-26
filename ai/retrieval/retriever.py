from aiohttp import payload
from ai.retrieval.processor import qdrant_client,COLLECTION_NAME
from ai.retrieval.embeddings import get_embeddings
from qdrant_client import models
from rich import print

query1 = "what is cohort model"


def retrieve_chunks(query:str, top_k:int = 5):
    """retrieve chunks from Qdrant based on query"""
    
    query_vector = get_embeddings([query])[0]

    result_chunks =[]
    
    response= qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )
    
    points = response.points
    
    for object in points:
        payload = object.payload
        text = payload['text']
        source = payload['source']
        result_chunks.append({"text": text, "source": source})
    
    return result_chunks 


print(retrieve_chunks(query1))