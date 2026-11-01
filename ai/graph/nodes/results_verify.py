import logfire
from ai.graph.states import ResearchState
from ai.graph.config import structured_llm_verify
from ai.graph.system_messages import system_messages_verification
from langchain.messages import HumanMessage

def results_verify(state:ResearchState):
    try:
        with logfire.span("verifying result "):
            search_results= state["search_results"]
            gathered_evidence = state["gathered_evidence"]



            human_message = HumanMessage(
            content=f"""
            Verify the following research output.

            Research Task:
            {state["research_plan"]}

            Result:
            {state["search_results"]}

            Gathered Evidence:
            {state["gathered_evidence"]}

            Evaluate the claims against the gathered evidence and return
            a structured VerificationResult.
            """
        )
            
            response = structured_llm_verify.invoke([system_messages_verification,human_message])
            response_dict= response.model_dump()
            print(response,"\n",type(response),type(response_dict))
            return {
                "verification_results":[response_dict]
            }
    except Exception:
        logfire.exception("verification failed")