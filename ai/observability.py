"""Observability configuration for ResearchPilotAI using Pydantic Logfire.

This module initializes OpenTelemetry tracing for LangChain / LangGraph,
configures Logfire (console + cloud dashboard if authenticated / token present),
and instruments HTTP clients (httpx, requests), Pydantic, and FastAPI.
"""

import os
import logging
from typing import Optional
import logfire

# 1. Enable OpenTelemetry export for LangChain and LangGraph before importing them
os.environ.setdefault("LANGSMITH_OTEL_ENABLED", "true")
os.environ.setdefault("LANGSMITH_OTEL_ONLY", "true")
os.environ.setdefault("LANGSMITH_TRACING", "true")

_configured = False


def setup_logfire(service_name: str = "researchpilotai", service_version: str = "0.1.0") -> logfire.Logfire:
    """Configure Logfire and instrument core libraries.

    Uses `send_to_logfire='if-token-present'` so that:
    - If LOGFIRE_TOKEN is set or user ran `logfire auth`, traces stream to the Logfire platform.
    - If no credentials exist, it outputs structured logs to console without blocking in interactive prompts.
    """
    global _configured
    if _configured:
        return logfire

    logfire.configure(
        service_name=service_name,
        service_version=service_version,
        send_to_logfire="if-token-present",
    )

    # Instrument outgoing HTTP clients (used by Qdrant, LangChain, Groq, Google GenAI, etc.)
    try:
        logfire.instrument_httpx()
    except Exception as e:
        logfire.warn("Could not instrument httpx: {error}", error=str(e))

    try:
        logfire.instrument_requests()
    except Exception as e:
        logfire.warn("Could not instrument requests: {error}", error=str(e))

    # Instrument Pydantic validation
    try:
        logfire.instrument_pydantic()
    except Exception as e:
        logfire.warn("Could not instrument pydantic: {error}", error=str(e))

    # Connect standard logging to Logfire
    logging.basicConfig(handlers=[logfire.LogfireLoggingHandler()], level=logging.INFO)

    _configured = True
    return logfire


def instrument_fastapi_app(app) -> None:
    """Instrument a FastAPI application instance with Logfire."""
    try:
        logfire.instrument_fastapi(app)
        logfire.info("FastAPI application instrumented with Logfire")
    except Exception as e:
        logfire.warn("Failed to instrument FastAPI app: {error}", error=str(e))


# Initialize on module import
setup_logfire()

__all__ = ["logfire", "setup_logfire", "instrument_fastapi_app"]
