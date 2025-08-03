from typing import List
from pydantic import BaseModel, Field


class Reference(BaseModel):
    """
    Represents a reference in the user prompt response.
    """
    statement: str = Field(..., description="A statement related to the prompt.")
    page_number: int = Field(..., description="Page number the chunk is from.")

class UserPromptResponse(BaseModel):
    """
    Response model for user prompt operations.
    """
    response: str = Field(..., description="The response generated for user's prompt.")
    references: List[Reference] = Field(default_factory=list, description="List of references related to the response.")
    concept_ids: List[str] = Field(default_factory=list, description="List of concept graph element (vertex/edge) ids related to the response.")

