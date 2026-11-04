import os
import logfire
from dotenv import load_dotenv
from qdrant_client import models

from ai.retrieval.embeddings import get_embeddings
from ai.retrieval.processor import COLLECTION_NAME, qdrant_client

load_dotenv()


def retrieve_chunks(
    query: str,
    top_k: int = 5,
    filename_filter: str | None = None,
    user_id: str | None = None,
    chat_id: str | None = None,
) -> list[dict]:
    """Retrieve top_k chunks from Qdrant based on semantic similarity to query,

    with optional filename, user_id, and chat_id filtering.
    """
    with logfire.span("retrieve_chunks", query=query, top_k=top_k, filename_filter=filename_filter):
        try:
            query_vector = get_embeddings([query])[0]
            resolved_user_id = user_id or os.getenv("USER_ID", "himanshu")
            resolved_chat_id = chat_id or os.getenv("CHAT_ID", "chat_1")

            must_conditions = [
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(value=resolved_user_id),
                ),
                models.FieldCondition(
                    key="chat_id",
                    match=models.MatchValue(value=resolved_chat_id),
                ),
            ]

            if filename_filter:
                clean_name = os.path.basename(filename_filter).strip()
                must_conditions.append(
                    models.FieldCondition(
                        key="source",
                        match=models.MatchValue(value=clean_name),
                    )
                )

            response = qdrant_client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                query_filter=models.Filter(must=must_conditions),
                limit=top_k,
                with_payload=True,
            )

            result_chunks = []
            for obj in response.points:
                payload = obj.payload or {}
                text = payload.get("text", "")
                source = payload.get("source", "unknown")
                source_type = payload.get("source_type", "")
                chunk_index = payload.get("chunk_index")
                total_chunks = payload.get("total_chunks")

                score = round(float(obj.score), 4) if hasattr(obj, "score") and obj.score is not None else None

                metadata = {
                    k: v
                    for k, v in payload.items()
                    if k not in ("text", "user_id", "chat_id") and v is not None
                }

                result_chunks.append({
                    "text": text,
                    "source": source,
                    "source_type": source_type,
                    "chunk_index": chunk_index,
                    "total_chunks": total_chunks,
                    "score": score,
                    "metadata": metadata,
                })

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
            logfire.exception("Failed to retrieve chunks from Qdrant: {error}", error=str(e), query=query)
            raise
