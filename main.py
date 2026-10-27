import uvicorn
import ai.observability  # noqa: F401
import logfire


def start():
    """Start the ResearchPilot AI FastAPI application server."""
    logfire.info("Starting ResearchPilot AI server with uvicorn...")
    uvicorn.run("ai.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
