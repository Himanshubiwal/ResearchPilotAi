import logfire
from ai.retrieval.processor import qdrant_client, COLLECTION_NAME
from ai.retrieval.embeddings import get_embeddings
from  qdrant_client import models
from dotenv import load_dotenv
import os

load_dotenv()


def retrieve_chunks(query: str, top_k: int = 5,user_id:str | None=None,chat_id:str | None=None) -> list[dict]:
    """Retrieve top_k chunks from Qdrant based on semantic similarity to query."""
    with logfire.span("retrieve_chunks: {query}", query=query, top_k=top_k):
        try:
            query_vector = get_embeddings([query])[0]
            if user_id is None:
                user_id = os.getenv("USER_ID")
            if chat_id is None:
                chat_id = os.getenv("CHAT_ID")
            response = qdrant_client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=user_id),
                        ),
                        models.FieldCondition(
                            key="chat_id",
                            match=models.MatchValue(value=chat_id),
                        ),
                    ]
                ),
                limit=top_k,
                with_payload=True,
            )

            result_chunks = []
            points = response.points

            for obj in points:
                payload = obj.payload or {}
                text = payload.get("text", "")
                source = payload.get("source", "unknown")
                result_chunks.append({"text": text, "source": source})

            sources = list({c["source"] for c in result_chunks})
            logfire.info(
                "Retrieved {count} relevant chunks from Qdrant",
                count=len(result_chunks),
                collection=COLLECTION_NAME,
                sources=sources,
                query=query,
            )
            return result_chunks
        except Exception as e:
            logfire.exception(f"Failed to retrieve chunks from Qdrant:{COLLECTION_NAME} {e}", error=str(e), query=query)
            raise
