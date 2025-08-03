from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared_utils.sql_models import IngestionJob

async def async_insert_ingestion_job(session: AsyncSession, ingestion_job: IngestionJob) -> None:
    """
    Asynchronously inserts a new ingestion job into the database.

    Args:
        session (AsyncSession): The async session to use for the insert operation.
        ingestion_job (IngestionJob): The ingestion job object to insert.

    Returns:
        None
    """
    session.add(ingestion_job)
    await session.commit()

async def async_get_ingestion_job(session: AsyncSession, job_id: UUID) -> Optional[IngestionJob]:
    """
    Asynchronously retrieves an ingestion job by its ID.

    Args:
        session (AsyncSession): The async session to use for the query.
        job_id (UUID): The ID of the ingestion job to retrieve.

    Returns:
        Optional[IngestionJob]: The ingestion job if found, otherwise None.
    """
    statement = select(IngestionJob).where(IngestionJob.job_id == job_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def async_update_ingestion_job_status(session: AsyncSession, job_id: UUID, status: str) -> None:
    """
    Asynchronously updates the status of an ingestion job.

    Args:
        session (AsyncSession): The async session to use for the update operation.
        job_id (UUID): The ID of the ingestion job to update.
        status (str): The new status to set for the ingestion job.

    Returns:
        None
    """
    statement = select(IngestionJob).where(IngestionJob.job_id == job_id)
    result = await session.execute(statement)
    ingestion_job = result.scalar_one_or_none()
    
    if ingestion_job:
        ingestion_job.status = status
        await session.commit()
    else:
        raise ValueError(f"Ingestion job with ID {job_id} not found.")
    
async def async_update_ingestion_job_content(session: AsyncSession, job_id: UUID, content: Dict[str, Any]) -> None:
    """
    Asynchronously updates the content of an ingestion job.

    Args:
        session (AsyncSession): The async session to use for the update operation.
        job_id (UUID): The ID of the ingestion job to update.
        content (Dict[str, Any]): The new content to set for the ingestion job.

    Returns:
        None
    """
    statement = select(IngestionJob).where(IngestionJob.job_id == job_id)
    result = await session.execute(statement)
    ingestion_job = result.scalar_one_or_none()
    
    if ingestion_job:
        ingestion_job.content = content
        await session.commit()
    else:
        raise ValueError(f"Ingestion job with ID {job_id} not found.")