from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared_utils.sql_models import DocumentMetadata

async def async_insert_document(session: AsyncSession, document_metadata: DocumentMetadata) -> None:
    """
    Asynchronously inserts a new document metadata entry into the database.

    Args:
        session (AsyncSession): The async session to use for the insert operation.
        document_metadata (DocumentMetadata): The document metadata object to insert.

    Returns:
        None
    """
    session.add(document_metadata)
    await session.commit()

async def async_get_document(session: AsyncSession, document_id: UUID) -> Optional[DocumentMetadata]:
    """
    Asynchronously retrieves a document by its ID.

    Args:
        session (AsyncSession): The async session to use for the query.
        document_id (UUID): The ID of the document to retrieve.

    Returns:
        Optional[DocumentMetadata]: The document metadata if found, otherwise None.
    """
    statement = select(DocumentMetadata).where(DocumentMetadata.document_id == document_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def async_get_all_documents(session: AsyncSession) -> List[DocumentMetadata]:
    """
    Asynchronously retrieves all document metadata entries from the database.

    Args:
        session (AsyncSession): The async session to use for the query.

    Returns:
        List[DocumentMetadata]: A list of all document metadata entries.
    """
    statement = select(DocumentMetadata)
    result = await session.execute(statement)
    return result.scalars().all()

async def async_update_document_status(session: AsyncSession, document_id: UUID, status: str) -> None:
    """
    Asynchronously updates the status of a document.

    Args:
        session (AsyncSession): The async session to use for the update operation.
        document_id (UUID): The ID of the document to update.
        status (str): The new status to set for the document.

    Returns:
        None
    """
    statement = select(DocumentMetadata).where(DocumentMetadata.document_id == document_id)
    result = await session.execute(statement)
    document = result.scalar_one_or_none()
    
    if document:
        document.status = status
        await session.commit()
    else:
        raise ValueError(f"Document with ID {document_id} not found.")