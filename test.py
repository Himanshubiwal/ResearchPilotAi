
from urllib import response
import os
from typing import Literal
from rich import print
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from ai.graph.config import structured_output_llm_gemini,llm_openrouter

load_dotenv()



# 6. Invoke the model
def main():


    response=llm_openrouter.invoke([HumanMessage(content="who are you ?")])
    
    print (response)
    # # 7. Print structured Pydantic output
    # print("\n========== PYDANTIC OUTPUT ==========\n")
    # print(result)
    # # 8. Access individual fields
    # print("\n========== ANSWER ==========\n")
    # print(result.content)
    # print(type(result.content))

    # print("\n========== EVIDENCE ==========\n")

    # for index, evidence in enumerate(result.evidence, start=1):
    #     print(f"\nEvidence {index}")
    #     print("Content:", evidence.content)
    #     print("Source:", evidence.source)
    #     print("Source Type:", evidence.source_type)
    #     print("Title:", evidence.title)
    #     print("Metadata:", evidence.metadata)

    # # 9. Convert Pydantic object into a Python dictionary
    # result_dict = result.model_dump()

    # print("\n========== PYTHON DICTIONARY ==========\n")
    # print(result_dict)
    # print(type(result_dict))


if __name__ == "__main__":
    main()
