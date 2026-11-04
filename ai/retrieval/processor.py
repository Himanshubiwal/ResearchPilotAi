import os
import sys
import time
import uuid
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
import logfire
from qdrant_client import QdrantClient, models

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.observability import setup_logfire
from ai.retrieval.chunking import text_splitter
from ai.retrieval.embeddings import get_embeddings
from ai.retrieval.loaders import (
    parse_pdf,
    parse_docx,
    parse_txt,
    parse_html,
    parse_json,
    parse_csv,
    parse_pptx,
)

load_dotenv()
setup_logfire()

user_id = os.getenv("USER_ID", "default_user")
chat_id = os.getenv("CHAT_ID", "default_chat")

qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=120,
    check_compatibility=False,
)

COLLECTION_NAME = "VECTOR_3"
VECTOR_SIZE = 3072  # gemini-embedding-001 outputs 3072 dimensions
BATCH_SIZE = 90  # Stay under Gemini free tier limit (100 req/min)

LOADER_MAP = {
    ".pdf": parse_pdf,
    ".docx": parse_docx,
    ".doc": parse_docx,
    ".txt": parse_txt,
    ".text": parse_txt,
    ".md": parse_txt,
    ".html": parse_html,
    ".htm": parse_html,
    ".json": parse_json,
    ".csv": parse_csv,
    ".pptx": parse_pptx,
    ".ppt": parse_pptx,
}


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

        # Ensure indexes for filterable fields
        for field in ["user_id", "chat_id", "source", "source_type"]:
            try:
                qdrant_client.create_payload_index(
                    collection_name=COLLECTION_NAME,
                    field_name=field,
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
            except Exception:
                pass


def store_vectors(chunks: list[str], filename: str, source_type: str, metadata: dict | None = None):
    """Generate embeddings and store text chunks with metadata in Qdrant in batches."""
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

                points = []
                for idx, (chunk, vector) in enumerate(zip(batch, embeddings), start=i):
                    payload = {
                        "user_id": user_id,
                        "chat_id": chat_id,
                        "text": chunk,
                        "source": filename,
                        "source_type": source_type,
                        "chunk_index": idx,
                        "total_chunks": len(chunks),
                    }
                    if metadata:
                        for k, v in metadata.items():
                            if k not in ("text", "user_id", "chat_id", "source", "source_type") and v is not None:
                                payload[k] = v

                    points.append(
                        models.PointStruct(
                            id=str(uuid.uuid4()),
                            vector=vector,
                            payload=payload,
                        )
                    )

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


def process_file(target_path: Path) -> bool:
    """Parse a single file, split into chunks, and store embeddings in Qdrant."""
    if not target_path.exists():
        logfire.error("File does not exist: {path}", path=str(target_path))
        return False

    ext = target_path.suffix.lower()
    parser = LOADER_MAP.get(ext)
    if not parser:
        logfire.warn("Skipping unsupported file format: {path}", path=str(target_path))
        return False

    filename = target_path.name
    with logfire.span("process_file", filename=filename, extension=ext):
        print(f"\n[+] Processing: {filename} ({ext})")
        loaded_text, metadata = parser(str(target_path))

        if not loaded_text or not loaded_text.strip():
            logfire.warn("No text extracted from file: {filename}", filename=filename)
            print(f"    [!] Warning: No text content found in {filename}")
            return False

        logfire.info(
            "Extracted text",
            filename=filename,
            character_count=len(loaded_text),
            metadata=metadata,
        )
        print(f"    Extracted {len(loaded_text)} characters.")

        chunks = text_splitter(loaded_text)
        logfire.info("Chunking completed", filename=filename, chunk_count=len(chunks))
        print(f"    Created {len(chunks)} chunks.")

        store_vectors(
            chunks=chunks,
            filename=filename,
            source_type=ext,
            metadata=metadata,
        )
        print(f"    Stored {len(chunks)} vectors in Qdrant successfully.")
        return True


def process_directory(directory: Path) -> dict:
    """Process all supported documents within a directory."""
    with logfire.span("process_directory", directory=str(directory)):
        if not directory.exists() or not directory.is_dir():
            logfire.error("Directory not found: {directory}", directory=str(directory))
            print(f"[!] Directory not found: {directory}")
            return {"total": 0, "succeeded": 0, "failed": 0, "files": []}

        # Filter supported files, ignore hidden and temporary lock files (e.g. ~$*.docx)
        supported_files = [
            f
            for f in sorted(directory.iterdir())
            if f.is_file()
            and not f.name.startswith((".", "~$"))
            and f.suffix.lower() in LOADER_MAP
        ]

        if not supported_files:
            logfire.warn("No supported documents found in directory: {directory}", directory=str(directory))
            print(f"[!] No supported documents found in: {directory}")
            return {"total": 0, "succeeded": 0, "failed": 0, "files": []}

        print(f"\n========================================================")
        print(f"Found {len(supported_files)} supported documents in '{directory}':")
        for idx, f in enumerate(supported_files, start=1):
            print(f"  {idx}. {f.name} ({f.suffix.lower()})")
        print(f"========================================================")

        succeeded = 0
        failed = 0
        for idx, f in enumerate(supported_files, start=1):
            print(f"\n({idx}/{len(supported_files)}) Starting {f.name}...")
            try:
                if process_file(f):
                    succeeded += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                logfire.exception("Error processing file {filename}: {error}", filename=f.name, error=str(e))
                print(f"    [X] Error processing {f.name}: {e}")

        summary = {
            "total": len(supported_files),
            "succeeded": succeeded,
            "failed": failed,
            "files": [f.name for f in supported_files],
        }
        logfire.info("Completed directory ingestion", **summary)
        print(f"\n========================================================")
        print(f"Ingestion Finished: {succeeded}/{len(supported_files)} succeeded, {failed} failed.")
        print(f"========================================================\n")
        return summary


def main():
    """Main CLI entrypoint. Ingests all files in 'data' directory or given paths."""
    with logfire.span("processor_run"):
        create_collection()

        default_data_dir = PROJECT_ROOT / "data"
        if not default_data_dir.exists():
            default_data_dir = Path("data")

        # If arguments provided, process each argument (file or dir)
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                p = Path(arg)
                if not p.exists():
                    p = default_data_dir / arg

                if p.is_dir():
                    process_directory(p)
                elif p.is_file():
                    process_file(p)
                else:
                    print(f"[!] Path not found: {arg}")
        else:
            # Default behavior: process all documents in data/ directory
            print(f"[i] No file specified. Processing all documents in '{default_data_dir}'...")
            process_directory(default_data_dir)

        qdrant_client.close()
        logfire.info("Processor finished and Qdrant connection closed.")


if __name__ == "__main__":
    main()
