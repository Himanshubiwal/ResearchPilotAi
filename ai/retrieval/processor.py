import os
import sys
import time
import uuid
from pathlib import Path
from dotenv import load_dotenv
import logfire
from qdrant_client import QdrantClient, models

from ai.observability import setup_logfire
from ai.retrieval.chunking import text_splitter
from ai.retrieval.embeddings import get_embeddings
from ai.retrieval.loaders.pdf_load import parse_pdf

load_dotenv()
setup_logfire()

user_id = os.getenv("USER_ID")
chat_id = os.getenv("CHAT_ID")


qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=120,
    check_compatibility=False,
)

COLLECTION_NAME = "VECTOR_3"
VECTOR_SIZE = 3072  # gemini-embedding-001 outputs 3072 dimensions
BATCH_SIZE = 90  # Stay under Gemini free tier limit (100 req/min)


def create_collection():
    """Ensure the Qdrant vector collection exists with the appropriate configuration."""
    with logfire.span("create_collection", collection=COLLECTION_NAME, vector_size=VECTOR_SIZE):
        if qdrant_client.collection_exists(COLLECTION_NAME):
            info = qdrant_client.get_collection(COLLECTION_NAME)
            current_size = info.config.params.vectors.size
            if current_size != VECTOR_SIZE:
                logfire.warn(
                    "Collection has wrong vector size ({current}), recreating with {expected}...",
                    current=current_size,
                    expected=VECTOR_SIZE,
                )
                qdrant_client.delete_collection(COLLECTION_NAME)

        if not qdrant_client.collection_exists(COLLECTION_NAME):
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=models.Distance.COSINE,
                ),
            )
            logfire.info(
                "Created Qdrant collection",
                collection=COLLECTION_NAME,
                vector_size=VECTOR_SIZE,
            )
        else:
            logfire.info("Qdrant collection verified and ready", collection=COLLECTION_NAME)


def store_vectors(chunks: list[str], filename: str, source_type: str):
    """Generate embeddings and store text chunks in Qdrant in batches with rate limit handling."""
    with logfire.span("store_vectors", filename=filename, total_chunks=len(chunks), source_type=source_type):
        if not chunks:
            logfire.warn("store_vectors called with empty chunks list", filename=filename)
            return

        total_stored = 0
        total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE

        for i in range(0, len(chunks), BATCH_SIZE):
            batch_num = (i // BATCH_SIZE) + 1
            batch = chunks[i : i + BATCH_SIZE]

            with logfire.span(
                "batch {batch_num}/{total_batches}",
                batch_num=batch_num,
                total_batches=total_batches,
                batch_size=len(batch),
            ):
                logfire.info(
                    "Embedding batch {batch_num}/{total_batches} ({count} chunks)",
                    batch_num=batch_num,
                    total_batches=total_batches,
                    count=len(batch),
                )
                embeddings = get_embeddings(batch)

                if len(batch) != len(embeddings):
                    raise ValueError(
                        f"Batch {batch_num}: chunks ({len(batch)}) and embeddings ({len(embeddings)}) count mismatch"
                    )

                points = [
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vector,
                        payload={
                            "user_id": user_id,
                            "chat_id": chat_id,
                            "text": chunk,
                            "source": filename,
                            "source_type": source_type,
                        },
                    )
                    for chunk, vector in zip(batch, embeddings)
                ]

                # Retry upsert up to 3 times on transient failures
                for attempt in range(1, 4):
                    try:
                        qdrant_client.upsert(
                            collection_name=COLLECTION_NAME,
                            points=points,
                        )
                        break
                    except Exception as e:
                        if attempt < 3:
                            logfire.warn(
                                "Upsert failed (attempt {attempt}/3): {error}. Retrying in 10s...",
                                attempt=attempt,
                                error=str(e),
                            )
                            time.sleep(10)
                        else:
                            logfire.exception("Upsert failed permanently on batch {batch_num}", batch_num=batch_num)
                            raise

                total_stored += len(points)
                logfire.info(
                    "Batch {batch_num}/{total_batches} stored {points} vectors (total: {total_stored})",
                    batch_num=batch_num,
                    total_batches=total_batches,
                    points=len(points),
                    total_stored=total_stored,
                )

                # Rate limit: wait before next batch (skip wait after last batch)
                if i + BATCH_SIZE < len(chunks):
                    logfire.info("Waiting 60s for Gemini API rate limits...")
                    time.sleep(60)

        logfire.info("Finished storing vectors", total_vectors=total_stored, filename=filename)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python -m ai.retrieval.processor <pdf_filename_in_data_dir>")
        sys.exit(1)

    filename = sys.argv[1]
    with logfire.span("CLI ingestion process", filename=filename):
        create_collection()
        target_path = Path("data") / filename
        if not target_path.exists():
            target_path = Path(filename)

        loaded_text = parse_pdf(str(target_path))
        logfire.info("Extracted text from PDF", character_count=len(loaded_text))

        chunks = text_splitter(loaded_text)
        logfire.info("Chunking completed", chunk_count=len(chunks))

        source_type = Path(filename).suffix
        store_vectors(
            chunks=chunks,
            filename=filename,
            source_type=source_type,
        )

        qdrant_client.close()
        logfire.info("Vector ingestion completed successfully for {filename}", filename=filename)