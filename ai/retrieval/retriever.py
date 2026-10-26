from ai.retrieval.processor import qdrant_client,COLLECTION_NAME
from ai.retrieval.embeddings import get_embeddings
from qdrant_client import models

query = "what is cohort model"


def retrieve_chunks(query:str, top_k:int = 5):
    """retrieve chunks from Qdrant based on query"""
    
    query_vector = get_embeddings([query])


    response= qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )
    