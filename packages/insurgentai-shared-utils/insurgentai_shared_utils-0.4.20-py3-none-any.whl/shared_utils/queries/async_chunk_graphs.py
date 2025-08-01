from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared_utils.sql_models import ChunkGraph

async def async_insert_chunk_graph(session: AsyncSession, graph: ChunkGraph) -> None:
    """
    Asynchronously inserts a new graph into the database.

    Args:
        session (AsyncSession): The async session to use for the insert operation.
        graph (ChunkGraph): The graph object to insert.

    Returns:
        None
    """
    session.add(graph)
    await session.commit()

async def async_get_chunk_graph(session: AsyncSession, graph_id: UUID) -> Optional[ChunkGraph]:
    """
    Asynchronously retrieves a graph by its ID.

    Args:
        session (AsyncSession): The async session to use for the query.
        graph_id (UUID): The ID of the graph to retrieve.

    Returns:
        Optional[ChunkGraph]: The graph data if found, otherwise None.
    """
    statement = select(ChunkGraph).where(ChunkGraph.graph_id == graph_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def async_get_chunk_graph_for_chunk(session: AsyncSession, chunk_id: UUID) -> Optional[ChunkGraph]:
    """
    Asynchronously retrieves the graph associated with a specific chunk.

    Args:
        session (AsyncSession): The async session to use for the query.
        chunk_id (UUID): The ID of the chunk.

    Returns:
        Optional[ChunkGraph]: The graph data if found, otherwise None.
    """
    statement = select(ChunkGraph).where(ChunkGraph.chunk_id == chunk_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def async_get_chunk_graphs_for_chunks(session: AsyncSession, chunk_ids: List[UUID]) -> List[ChunkGraph]:
    """
    Asynchronously retrieves the graphs associated with specific chunks.

    Args:
        session (AsyncSession): The async session to use for the query.
        chunk_ids (List[UUID]): The IDs of the chunks.

    Returns:
        List[ChunkGraph]: The list of graph data if found, otherwise an empty list.
    """
    statement = select(ChunkGraph).where(ChunkGraph.chunk_id.in_(chunk_ids))
    result = await session.execute(statement)
    return result.scalars().all() or []