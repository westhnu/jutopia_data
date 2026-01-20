from typing import List
from pydantic import BaseModel, Field


class Source(BaseModel):
    """Schema for a source used by the ReAct Agent"""

    url: str = Field(description="The url of the source")


class AgentResponse(BaseModel):
    """Schema for agent response with answer and sources"""

    answer: str = Field(description="The agent's answer to the query")
    sources: List[Source] = Field(
        description="List of sources used to generate the answer"
    )
