from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logfire
from ai.observability import setup_logfire, instrument_fastapi_app
from ai.graph.workflow import ask_ai



setup_logfire()

app = FastAPI(
    title="ResearchPilot AI API",
    description="FastAPI service for ResearchPilot AI assistant powered by LangGraph, Groq, and Logfire observability.",
    version="0.1.0",
)

# Instrument FastAPI with Logfire
instrument_fastapi_app(app)


class QueryModel(BaseModel):
    question: str


@app.get("/")
def root():
    logfire.info("Health check ping received")
    return {"message": "ResearchPilot AI API is running"}


@app.post("/query")
def query(query: QueryModel):
    question = query.question
    with logfire.span("Process query endpoint: {question}", question=question):
        logfire.info("Received query request", question=question)
        try:
            result = ask_ai(question)
            logfire.info("Query answered successfully", question=question, answer_preview=str(result)[:100])
            return {"answer": result}
        except Exception as e:
            logfire.exception("Error processing query: {error}", error=str(e), question=question)
            raise HTTPException(status_code=500, detail=str(e))