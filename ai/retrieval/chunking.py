from typing import List
import logfire
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True,
)


def text_splitter(text: str) -> List[str]:
    """Split input text into overlapping chunks using RecursiveCharacterTextSplitter."""
    with logfire.span("text_splitter", input_chars=len(text), chunk_size=1000, chunk_overlap=200):
        chunks = splitter.split_text(text)
        logfire.info(
            "Text chunking completed",
            input_chars=len(text),
            chunks_count=len(chunks),
        )
        return chunks