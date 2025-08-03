from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared_utils.sql_models import Layout


async def async_layout_exists(session: AsyncSession, graph_name: str, layout_name: str) -> bool:
    """
    Asynchronously checks if a layout with the given graph name and layout name exists.

    Args:
        session (AsyncSession): The async session to use for the query.
        graph_name (str): The name of the graph to check.
        layout_name (str): The name of the layout to check.

    Returns:
        bool: True if the layout exists, False otherwise.
    """
    statement = select(Layout).where(
        Layout.graph_name == graph_name, Layout.layout_name == layout_name
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none() is not None


async def async_get_layout(session: AsyncSession, graph_id: UUID, layout_name: str) -> Optional[Layout]:
    """
    Asynchronously retrieves a specific layout by graph ID and layout name.

    Args:
        session (AsyncSession): The async session to use for the query.
        graph_id (UUID): The ID of the graph to retrieve the layout for.
        layout_name (str): The name of the layout to retrieve.

    Returns:
        Optional[Layout]: The layout object if found, otherwise None.
    """
    statement = select(Layout).where(
        Layout.graph_id == graph_id, Layout.layout_name == layout_name
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def async_get_layouts(session: AsyncSession, graph_name: str) -> List[Layout]:
    """
    Asynchronously retrieves all layouts for a specific graph.

    Args:
        session (AsyncSession): The async session to use for the query.
        graph_name (str): The name of the graph to retrieve layouts for.

    Returns:
        List[Layout]: A list of layouts for the specified graph.
    """
    statement = select(Layout).where(Layout.graph_name == graph_name)
    result = await session.execute(statement)
    return result.scalars().all() or []


async def async_insert_layout(session: AsyncSession, layout: Layout) -> None:
    """
    Asynchronously inserts a new layout into the database.

    Args:
        session (AsyncSession): The async session to use for the insert operation.
        layout (Layout): The layout object to insert.

    Returns:
        None
    """
    session.add(layout)
    await session.commit()