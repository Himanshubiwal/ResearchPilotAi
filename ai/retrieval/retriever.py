import logfire
from ai.retrieval.processor import qdrant_client, COLLECTION_NAME
from ai.retrieval.embeddings import get_embeddings


def retrieve_chunks(query: str, top_k: int = 5) -> list[dict]:
    """Retrieve top_k chunks from Qdrant based on semantic similarity to query."""
    with logfire.span("retrieve_chunks: {query}", query=query, top_k=top_k):
        try:
            query_vector = get_embeddings([query])[0]

            response = qdrant_client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
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
            logfire.exception("Failed to retrieve chunks from Qdrant: {error}", error=str(e), query=query)
            raise
