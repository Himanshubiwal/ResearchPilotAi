import os
import re
import sys
import time
from typing import List
from dotenv import load_dotenv
import logfire
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

EMBEDDING_MODEL = "gemini-embedding-001"

model_embedding = GoogleGenerativeAIEmbeddings(
    google_api_key=os.getenv("GEMINI_API_KEY"),
    model=EMBEDDING_MODEL,
)


def get_embeddings(batch: List[str]) -> List[List[float]]:
    """Generate embedding vectors using Google Generative AI embeddings with rate-limit handling."""
    with logfire.span("get_embeddings", batch_size=len(batch), model=EMBEDDING_MODEL):
        max_retries = 6
        for attempt in range(1, max_retries + 1):
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
                err_msg = str(e)
                if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
                    delay = 60
                    delay_match = re.search(r"retry in ([\d\.]+)s", err_msg)
                    if delay_match:
                        delay = int(float(delay_match.group(1))) + 5

                    logfire.warn(
                        "Gemini rate limit 429 hit (attempt {attempt}/{max_retries}). Sleeping {delay}s...",
                        attempt=attempt,
                        max_retries=max_retries,
                        delay=delay,
                    )
                    print(f"    [!] Gemini rate limit hit. Waiting {delay}s before retrying attempt {attempt}/{max_retries}...")
                    time.sleep(delay)
                else:
                    if attempt < max_retries:
                        logfire.warn("Transient embedding error (attempt {attempt}): {err}", attempt=attempt, err=err_msg)
                        time.sleep(10)
                    else:
                        logfire.exception("Embedding generation failed permanently: {error}", error=err_msg, batch_size=len(batch))
                        raise
