from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared_utils.sql_models.Chunk import Chunk

async def async_insert_chunk(session: AsyncSession, chunk: Chunk) -> None:
    """
    Asynchronously inserts a new chunk into the database.
    
    Args:
        session (AsyncSession): The async session to use for the insert operation.
        chunk (Chunk): The chunk object to insert.

    Returns:
        None
    """
    session.add(chunk)
    await session.commit()

async def async_insert_chunks(session: AsyncSession, chunks: List[Chunk]) -> None:
    """
    Asynchronously inserts multiple chunks into the database.
    
    Args:
        session (AsyncSession): The async session to use for the insert operation.
        chunks (List[Chunk]): A list of chunk objects to insert.

    Returns:
        None
    """
    session.add_all(chunks)
    await session.commit()

async def async_get_chunk(session: AsyncSession, chunk_id: UUID) -> Optional[Chunk]:
    """
    Asynchronously retrieves a chunk by its ID.
    
    Args:
        session (AsyncSession): The async session to use for the query.
        chunk_id (UUID): The ID of the chunk to retrieve.

    Returns:
        Optional[Chunk]: The chunk data if found, otherwise None.
    """
    statement = select(Chunk).where(Chunk.chunk_id == chunk_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def async_get_all_chunks_from_doc(session: AsyncSession, document_id: UUID) -> List[Chunk]:
    """
    Asynchronously retrieves all chunks that belong to a specific document.
    
    Args:
        session (AsyncSession): The async session to use for the query.
        document_id (UUID): The ID of the document to get chunks for.

    Returns:
        List[Chunk]: A list of all chunks belonging to the specified document.
    """
    statement = select(Chunk).where(Chunk.document_id == document_id)
    result = await session.execute(statement)
    return result.scalars().all()

async def async_update_chunk_graph_id(session: AsyncSession, chunk_id: UUID, graph_id: UUID) -> None:
    """
    Asynchronously updates the graph ID of a chunk.
    
    Args:
        session (AsyncSession): The async session to use for the update operation.
        chunk_id (UUID): The ID of the chunk to update.
        graph_id (UUID): The new graph ID to set.

    Returns:
        None
    """
    statement = select(Chunk).where(Chunk.chunk_id == chunk_id)
    result = await session.execute(statement)
    chunk = result.scalar_one_or_none()
    
    if chunk:
        chunk.graph_id = graph_id
        session.add(chunk)
        await session.commit()