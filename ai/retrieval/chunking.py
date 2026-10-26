from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True
)


def text_splitter(text:str)->List[str]:
    chunks=splitter.split_text(text)
    print("done babe")
    return chunks 