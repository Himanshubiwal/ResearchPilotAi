import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logfire
from ai.observability import setup_logfire, instrument_fastapi_app
from ai.graph.workflow import ask_ai
from ai.retrieval.processor import process_file, create_collection

setup_logfire()

app = FastAPI(
    title="ResearchPilot AI API",
    description="FastAPI service for ResearchPilot AI assistant powered by LangGraph, Groq, and Logfire observability.",
    version="0.1.0",
)

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrument FastAPI with Logfire
instrument_fastapi_app(app)

# Ensure data directory exists
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
def on_startup():
    """Ensure vector collection is initialized when FastAPI starts."""
    try:
        create_collection()
        logfire.info("Verified Qdrant vector collection on startup")
    except Exception as e:
        logfire.warn("Could not verify Qdrant collection on startup: {error}", error=str(e))


class QueryModel(BaseModel):
    question: str


@app.get("/")
def root():
    logfire.info("Health check ping received")
    return {"message": "ResearchPilot AI API is running"}


@app.post("/query")
def query(query: QueryModel):
    """Legacy text-only query endpoint."""
    question = query.question
    with logfire.span("Process query endpoint: {question}", question=question):
        logfire.info("Received query request", question=question)
        try:
            result = ask_ai(question)
            if isinstance(result, tuple):
                result, _ = result
            logfire.info("Query answered successfully", question=question, answer_preview=str(result)[:100])
            return {"answer": result}
        except Exception as e:
            logfire.exception("Error processing query: {error}", error=str(e), question=question)
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat_endpoint(
    query: str = Form(""),
    files: Optional[List[UploadFile]] = File(None),
):
    """
    Unified chat endpoint accepting both query text and document uploads.
    - Saves uploaded documents directly into the `data/` folder.
    - Immediately indexes them into the Qdrant vector store.
    - Runs the LangGraph AI research workflow to answer the query.
    """
    processed_files = []
    failed_files = []

    # 1. Handle document uploads and immediate indexing
    if files:
        for file in files:
            if not file.filename:
                continue
            dest_path = DATA_DIR / file.filename
            try:
                with open(dest_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                logfire.info("Saved file directly to data folder", filename=file.filename, path=str(dest_path))

                # Immediately index into Qdrant vector store
                indexed = process_file(dest_path)
                if indexed:
                    processed_files.append(file.filename)
                    logfire.info("Indexed file into Qdrant", filename=file.filename)
                else:
                    failed_files.append(file.filename)
                    logfire.warn("Indexing returned False", filename=file.filename)
            except Exception as e:
                failed_files.append(file.filename)
                logfire.exception("Error processing upload {filename}: {error}", filename=file.filename, error=str(e))

    # 2. Determine prompt for AI
    user_query = query.strip()
    if not user_query:
        if processed_files:
            user_query = f"Please provide a comprehensive summary and key takeaways of the uploaded document(s): {', '.join(processed_files)}."
        else:
            raise HTTPException(status_code=400, detail="A query prompt or document attachment is required.")

    # 3. Call ask_ai LangGraph workflow
    try:
        with logfire.span("chat_endpoint: ask_ai", query=user_query, processed_files=processed_files):
            logfire.info("Executing AI workflow with prompt", prompt=user_query, files=processed_files)
            res = ask_ai(user_query)
            if isinstance(res, tuple):
                answer, tool_count = res
            else:
                answer, tool_count = res, 0

            return {
                "response": answer,
                "tool_count": tool_count,
                "files_processed": processed_files,
                "files_failed": failed_files,
                "status": "success",
            }
    except Exception as e:
        logfire.exception("Error during AI execution: {error}", error=str(e), query=user_query)
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")
