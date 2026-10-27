import ai.observability  # noqa: F401
import logfire


def main() -> None:
    """CLI script entrypoint for researchpilotai."""
    logfire.info("ResearchPilot AI CLI entrypoint invoked")
    print("ResearchPilot AI is running with Logfire observability configured.")
