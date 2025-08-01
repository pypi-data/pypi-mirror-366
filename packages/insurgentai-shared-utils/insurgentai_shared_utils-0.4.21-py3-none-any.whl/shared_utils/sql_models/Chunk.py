from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID

class Chunk(SQLModel, table=True):
    """
    Represents a chunk of a document.
    """
    __tablename__ = "chunks"
    chunk_id: UUID = Field(primary_key=True, description="The unique identifier for the chunk.")
    document_id: UUID = Field(foreign_key="documentmetadata.document_id",index=True, description="The source document id.")
    text: str = Field(description="The text content of the chunk.")
    page_number: int = Field(description="The page number in the source document this chunk was created from.")
    graph_id : Optional[UUID] = Field(default=None, description="The unique identifier for the graph associated with the chunk.")