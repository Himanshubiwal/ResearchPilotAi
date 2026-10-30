from pydantic import BaseModel,Field
from typing import List



class Evidence(BaseModel):
    content: str
    source: str
    source_type: str
    title: str
    metadata: dict

class TaskResults(BaseModel):
    content :str = Field(description="these is task result content ")
    evidence :List[Evidence] = Field(description="these are the evidence of task results")


