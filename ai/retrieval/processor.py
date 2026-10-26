from qdrant_client import QdrantClient ,models
from dotenv import load_dotenv
import os
import uuid
import time 
from ai.retrieval.embeddings import get_embeddings
from ai.retrieval.chunking import text_splitter 
from ai.retrieval.loaders.pdf_load import parse_pdf


load_dotenv()

qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=120,
)

COLLECTION_NAME = "VECTOR_2"

def create_collection():
    VECTOR_SIZE = 3072  # gemini-embedding-001 outputs 3072 dimensions

    if qdrant_client.collection_exists(COLLECTION_NAME):
        info = qdrant_client.get_collection(COLLECTION_NAME)
        if info.config.params.vectors.size != VECTOR_SIZE:
            print(f"Collection has wrong vector size ({info.config.params.vectors.size}), recreating with {VECTOR_SIZE}...")
            qdrant_client.delete_collection(COLLECTION_NAME)

    if not qdrant_client.collection_exists(COLLECTION_NAME):
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )
        print(f"Collection '{COLLECTION_NAME}' created with size {VECTOR_SIZE}.")



BATCH_SIZE = 90  # Stay under Gemini free tier limit (100 req/min)

def store_vectors(chunks: list[str], filename: str, source_type: str):
    """Generate embeddings and store text chunks in Qdrant in batches."""

    if not chunks:
        print("No chunks to store.")
        return

    total_stored = 0
    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(chunks), BATCH_SIZE):
        batch_num = (i // BATCH_SIZE) + 1
        batch = chunks[i : i + BATCH_SIZE]

        print(f"Batch {batch_num}/{total_batches}: Embedding {len(batch)} chunks...")
        embeddings = get_embeddings(batch)

        if len(batch) != len(embeddings):
            raise ValueError(f"Batch {batch_num}: chunks ({len(batch)}) and embeddings ({len(embeddings)}) count mismatch")

        points = [
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
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
                    print(f"  Upsert failed (attempt {attempt}/3): {e}. Retrying in 10s...")
                    time.sleep(10)
                else:
                    raise

        total_stored += len(points)
        print(f"Batch {batch_num}/{total_batches}: Stored {len(points)} vectors. Total: {total_stored}")

        # Rate limit: wait before next batch (skip wait after last batch)
        if i + BATCH_SIZE < len(chunks):
            print("Waiting 60s for rate limit...")
            time.sleep(60)

    print(f"Done! Stored {total_stored} vectors total in Qdrant.")





if __name__ == "__main__":
    create_collection()

    sample_chunks = [
        "Qdrant is a vector database.",
        "Embeddings represent text as numerical vectors.",
    ]
    loaded_text = parse_pdf(r"D:\AnitGravity\ResearchPilotAi\data\fourth.pdf")
    print(f"Extracted {len(loaded_text)} chars")
    
    chunks= text_splitter(loaded_text)
    print(f"Created {len(chunks)} chunks")
    
    store_vectors(
        chunks=chunks,
        filename="fourth.pdf",
        source_type="pdf",
    )
 
    qdrant_client.close()