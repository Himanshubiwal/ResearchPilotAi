import logfire
from ai.graph.config import llm_groq
from langchain_core.messages import HumanMessage
from ai.retrieval.retriever import retrieve_chunks
from ai.graph.states import ResearchState


def add_human_message(state: ResearchState):
    question = state.get("question", "")
    with logfire.span("node:add_human_message", question=question):
        retrieved_chunks = retrieve_chunks(question)
        context = " ".join([chunk["text"] for chunk in retrieved_chunks])

        logfire.info(
            "Prepared context for query",
            question=question,
            chunks_count=len(retrieved_chunks),
            context_length=len(context),
            sources=list({chunk.get("source", "unknown") for chunk in retrieved_chunks}),
        )

        human_message = HumanMessage(
            content=f"""
        question :{question},
        context :{context}
        """
        )

        return {"messages": [human_message]}


def get_response(state: ResearchState):
    messages = state.get("messages", [])
    with logfire.span("node:get_response", message_count=len(messages)):
        logfire.info("Calling Groq LLM with messages", count=len(messages))
        response = llm_groq.invoke(messages)
        content_preview = str(response.content)[:120] if hasattr(response, "content") else ""
        logfire.info("LLM response generated", response_preview=content_preview)
        return {"messages": [response]}