import os
from typing import List
from dotenv import load_dotenv
import logfire
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

EMBEDDING_MODEL = "gemini-embedding-001"

model_embedding = GoogleGenerativeAIEmbeddings(
    google_api_key=os.getenv("GEMINI_API_KEY"),
    model=EMBEDDING_MODEL,
)


def get_embeddings(batch: List[str]) -> List[List[float]]:
    """Generate embedding vectors using Google Generative AI embeddings."""
    with logfire.span("get_embeddings", batch_size=len(batch), model=EMBEDDING_MODEL):
        try:
            embeddings = model_embedding.embed_documents(batch)
            dim = len(embeddings[0]) if embeddings else 0
            logfire.info(
                "Successfully generated embeddings",
                batch_size=len(batch),
                vector_dimension=dim,
                model=EMBEDDING_MODEL,
            )
            return embeddings
        except Exception as e:
            logfire.exception("Embedding generation failed: {error}", error=str(e), batch_size=len(batch))
            raise
