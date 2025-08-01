from uuid import UUID
from pydantic import BaseModel, Field

class KnowledgeGraphUpdatedEvent(BaseModel):
    """
    Event triggered when the knowledge graph is updated.
    """
    job_id: UUID = Field(..., description="Unique identifier for the job associated with the document ingestion")
    document_id: UUID = Field(..., description="Unique identifier for the document that was ingested")
    #NOTE: Apache AGE doesnt support UUID, so we use a string here
    kg_name: str = Field(..., description="Unique name for the knowledge graph that was updated")