from typing import Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import logfire

from ai.retrieval.retriever import retrieve_chunks


class DocRetrievalInput(BaseModel):
    query: str = Field(
        ...,
        description=(
            "The specific semantic search query or question to locate relevant information "
            "within user-provided research documents, reports, notes, or uploaded files. "
            "Use natural descriptive language rather than single keywords."
        ),
    )
    filename_filter: Optional[str] = Field(
        default=None,
        description=(
            "Optional document filename to search within (e.g. 'resume.docx', "
            "'fourth.pdf', 'Rag.docx', 'long_form_research_notes.txt', 'monthly_energy_metrics.csv'). "
            "Leave None to search across all uploaded documents."
        ),
    )
    top_k: Optional[int] = Field(
        default=5,
        description="Number of most relevant excerpts/chunks to retrieve (default is 5, max 10).",
    )


@tool("doc_retrieval", args_schema=DocRetrievalInput)
def doc_retrieval(query: str, filename_filter: Optional[str] = None, top_k: int = 5) -> str:
    """Search and retrieve factual evidence, excerpts, data, and context from local uploaded documents
and research files (PDF, DOCX, TXT, CSV, PPTX, HTML, JSON).

WHEN TO USE:
- The task requires information from user-provided files, internal project documents, uploaded reports, notes, or datasets.
- Looking for specific statistics, quotes, tables, facts, or methodology described in local files.

WHEN NOT TO USE:
- Do NOT use for real-time web news, current stock prices, or general public internet info (use web_search instead).

RETURNS:
- Formatted text containing numbered relevant excerpts with source citations and similarity scores,
  or a helpful guidance message if no matching content was found.
"""
    logfire.info("Document retrieval started", query=query, filename_filter=filename_filter, top_k=top_k)
    try:
        retrieved_chunks = retrieve_chunks(
            query=query,
            top_k=top_k,
            filename_filter=filename_filter,
        )

        logfire.info(
            "Document Retrieval Completed",
            chunks_count=len(retrieved_chunks),
            query=query,
        )

        if not retrieved_chunks:
            if filename_filter:
                return (
                    f"No relevant content found in '{filename_filter}' for query: '{query}'. "
                    "Try removing the filename filter or rephrasing the query."
                )
            return (
                f"No relevant content found in user documents for query: '{query}'. "
                "Try rephrasing your search query, or use web_search if this information requires external internet sources."
            )

        formatted_results = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            source = chunk.get("source", "unknown")
            score = chunk.get("score")
            score_str = f" | Relevance: {score:.2f}" if score is not None else ""
            meta = chunk.get("metadata", {})

            extra_meta = []
            if "total_pages" in meta:
                extra_meta.append(f"Pages: {meta['total_pages']}")
            if chunk.get("chunk_index") is not None and chunk.get("total_chunks") is not None:
                extra_meta.append(f"Chunk: {chunk['chunk_index'] + 1}/{chunk['total_chunks']}")

            meta_str = f" ({', '.join(extra_meta)})" if extra_meta else ""
            text = chunk.get("text", "").strip()

            formatted_results.append(
                f"--- Excerpt {i} [Source: {source}{score_str}{meta_str}] ---\n{text}"
            )

        return "\n\n".join(formatted_results)

    except Exception as e:
        logfire.exception("Document retrieval failed: {error}", error=str(e), query=query)
        raise
