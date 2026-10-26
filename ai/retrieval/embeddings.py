from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

model_embedding = GoogleGenerativeAIEmbeddings(
        google_api_key=os.getenv("GEMINI_API_KEY"),
        model="gemini-embedding-001"
    )
def get_embeddings(batch:List[str])->List[List[float]]:
    embeddings = model_embedding.embed_documents(batch)

    print("done babe2")
    return embeddings 
