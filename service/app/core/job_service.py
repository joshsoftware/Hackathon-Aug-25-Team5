import asyncio
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Union
from concurrent.futures import ThreadPoolExecutor, Future
from functools import wraps
import traceback

# Third-party imports
from sqlalchemy import Column, String, Text, TIMESTAMP, Enum
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from pydantic import BaseModel, ConfigDict
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()


# SQLAlchemy Model for Jobs table
class Job(Base):
    __tablename__ = 'jobs'

    job_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(PG_UUID(as_uuid=True), nullable=True)
    job_type = Column(String(50), nullable=False)
    status = Column(Enum('scheduled', 'in_progress', 'done', 'failed', name='job_status'), 
                   default='scheduled')
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    started_at = Column(TIMESTAMP, nullable=True)
    finished_at = Column(TIMESTAMP, nullable=True)
    result = Column(JSONB, default={})
    error_message = Column(Text, nullable=True)
    property_id = Column(PG_UUID(as_uuid=True), nullable=True)


# Pydantic Models for Job operations
class JobCreate(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True
    )
    
    job_type: str
    document_id: Optional[uuid.UUID] = None
    property_id: Optional[uuid.UUID] = None
    initial_data: Optional[Dict[str, Any]] = None


class JobUpdate(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True
    )
    
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class JobService:
    def __init__(self):
        """Initialize the JobService with async database connection"""
        self.database_url, use_ssl_connection = self._get_database_url()
        
        connect_args = {
            "server_settings": {
                "jit": "off"
            }
        }

        if use_ssl_connection:
            connect_args["ssl"] = "require"

        # Create async engine for Neon PostgreSQL
        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args=connect_args
        )

        # Create async session factory
        self.async_session = lambda: AsyncSession(
            bind=self.engine,
            expire_on_commit=False
        )
        
        # Thread pool executor for running jobs
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Store active jobs
        self.active_jobs: Dict[uuid.UUID, Future] = {}

    def _get_database_url(self) -> tuple[str, bool]:
        """Get database URL from environment variables"""
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError(
                "DATABASE_URL not found in environment variables. "
                "Please ensure your .env file contains the Neon PostgreSQL connection string."
            )

        use_ssl = False
        asyncpg_incompatible_params = [
            'sslmode', 'sslcert', 'sslkey', 'sslrootcert', 'sslcrl',
            'channel_binding', 'gssencmode', 'krbsrvname', 'gsslib',
            'service', 'passfile', 'requiressl', 'prefer_prepared_statements'
        ]

        if database_url.startswith(('postgresql://', 'postgres://')):
            parsed_url = urlparse(database_url)
            query_params = parse_qs(parsed_url.query)

            ssl_mode = query_params.get('sslmode', ['require'])[0]
            use_ssl = ssl_mode.lower() not in ('disable', 'allow')

            for param in asyncpg_incompatible_params:
                query_params.pop(param, None)

            new_query = urlencode(query_params, doseq=True)
            database_url = urlunparse(
                parsed_url._replace(scheme='postgresql+asyncpg', query=new_query)
            )

        elif database_url.startswith('postgresql+asyncpg://'):
            parsed_url = urlparse(database_url)
            query_params = parse_qs(parsed_url.query)

            ssl_mode = query_params.get('sslmode', ['require'])[0]
            use_ssl = ssl_mode.lower() not in ('disable', 'allow')

            for param in asyncpg_incompatible_params:
                query_params.pop(param, None)

            new_query = urlencode(query_params, doseq=True)
            database_url = urlunparse(parsed_url._replace(query=new_query))

        logger.info(f"Successfully processed database URL. SSL enabled: {use_ssl}")
        return database_url, use_ssl

    async def init_database(self):
        """Initialize database tables"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Job database tables initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing job database: {e}")
            raise

    async def create_job(self, job_data: JobCreate) -> Job:
        """Create a new job entry in the database"""
        try:
            async with self.async_session() as session:
                job = Job(
                    job_type=job_data.job_type,
                    document_id=job_data.document_id,
                    property_id=job_data.property_id,
                    result=job_data.initial_data or {},
                    status='scheduled'
                )
                
                session.add(job)
                await session.commit()
                await session.refresh(job)
                
                logger.info(f"Created job {job.job_id} of type {job.job_type}")
                return job
                
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            raise

    async def update_job_status(self, job_id: uuid.UUID, update_data: JobUpdate) -> Job:
        """Update job status and other details"""
        try:
            async with self.async_session() as session:
                from sqlalchemy import select, update
                
                # Get the job
                result = await session.execute(
                    select(Job).where(Job.job_id == job_id)
                )
                job = result.scalar_one_or_none()
                
                if not job:
                    raise ValueError(f"Job {job_id} not found")
                
                # Update fields
                if update_data.status is not None:
                    job.status = update_data.status
                if update_data.started_at is not None:
                    job.started_at = update_data.started_at
                if update_data.finished_at is not None:
                    job.finished_at = update_data.finished_at
                if update_data.result is not None:
                    job.result = update_data.result
                if update_data.error_message is not None:
                    job.error_message = update_data.error_message
                
                await session.commit()
                await session.refresh(job)
                
                logger.info(f"Updated job {job_id} status to {job.status}")
                return job
                
        except Exception as e:
            logger.error(f"Error updating job {job_id}: {e}")
            raise

    async def get_job(self, job_id: uuid.UUID) -> Optional[Job]:
        """Retrieve a job by ID"""
        try:
            async with self.async_session() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(Job).where(Job.job_id == job_id)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error retrieving job {job_id}: {e}")
            raise

    async def get_jobs_by_status(self, status: str) -> list[Job]:
        """Retrieve jobs by status"""
        try:
            async with self.async_session() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(Job).where(Job.status == status)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error retrieving jobs by status {status}: {e}")
            raise

    async def get_all_jobs(self) -> list[Job]:
        """Retrieve all jobs"""
        try:
            async with self.async_session() as session:
                from sqlalchemy import select
                result = await session.execute(select(Job))
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error retrieving all jobs: {e}")
            raise

    def run_job_async(self, job_id: uuid.UUID, task_func: Callable, *args, **kwargs) -> Future:
        """Run a job asynchronously using ThreadPoolExecutor"""
        try:
            # Submit the task to the thread pool
            future = self.executor.submit(task_func, *args, **kwargs)
            
            # Store the active job
            self.active_jobs[job_id] = future
            
            logger.info(f"Started async job {job_id}")
            return future
            
        except Exception as e:
            logger.error(f"Error starting async job {job_id}: {e}")
            raise

    async def start_job(self, job_id: uuid.UUID):
        """Mark job as started"""
        await self.update_job_status(
            job_id, 
            JobUpdate(status='in_progress', started_at=datetime.utcnow())
        )

    async def complete_job(self, job_id: uuid.UUID, result: Dict[str, Any]):
        """Mark job as completed successfully"""
        await self.update_job_status(
            job_id,
            JobUpdate(
                status='done',
                finished_at=datetime.utcnow(),
                result=result
            )
        )
        
        # Remove from active jobs
        if job_id in self.active_jobs:
            del self.active_jobs[job_id]

    async def fail_job(self, job_id: uuid.UUID, error_message: str):
        """Mark job as failed"""
        await self.update_job_status(
            job_id,
            JobUpdate(
                status='failed',
                finished_at=datetime.utcnow(),
                error_message=error_message
            )
        )
        
        # Remove from active jobs
        if job_id in self.active_jobs:
            del self.active_jobs[job_id]

    def is_job_running(self, job_id: uuid.UUID) -> bool:
        """Check if a job is currently running"""
        return job_id in self.active_jobs

    def get_job_result(self, job_id: uuid.UUID) -> Optional[Any]:
        """Get the result of a completed job"""
        if job_id in self.active_jobs:
            future = self.active_jobs[job_id]
            if future.done():
                try:
                    return future.result()
                except Exception as e:
                    logger.error(f"Error getting result for job {job_id}: {e}")
                    return None
        return None

    async def cancel_job(self, job_id: uuid.UUID) -> bool:
        """Cancel a running job"""
        if job_id in self.active_jobs:
            future = self.active_jobs[job_id]
            if not future.done():
                future.cancel()
                await self.fail_job(job_id, "Job cancelled by user")
                logger.info(f"Cancelled job {job_id}")
                return True
        return False

    async def close(self):
        """Close the service and cleanup resources"""
        # Cancel all running jobs
        for job_id in list(self.active_jobs.keys()):
            await self.cancel_job(job_id)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Close database connection
        await self.engine.dispose()
        logger.info("Job service closed")


# Decorator for easy job execution
def run_as_job(job_type: str, document_id: Optional[uuid.UUID] = None, 
                property_id: Optional[uuid.UUID] = None):
    """Decorator to run a function as a tracked job"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            job_service = JobService()
            job = None
            
            try:
                # Create job entry
                job = await job_service.create_job(JobCreate(
                    job_type=job_type,
                    document_id=document_id,
                    property_id=property_id
                ))
                
                # Mark job as started
                await job_service.start_job(job.job_id)
                
                # Run the actual function
                result = await func(*args, **kwargs)
                
                # Mark job as completed
                await job_service.complete_job(job.job_id, {"result": result})
                
                return result
                
            except Exception as e:
                if job:
                    error_msg = f"Error in job execution: {str(e)}\n{traceback.format_exc()}"
                    await job_service.fail_job(job.job_id, error_msg)
                raise
            finally:
                await job_service.close()
                
        return wrapper
    return decorator


# Example usage functions
async def example_long_running_task(task_id: int, delay: int = 3) -> Dict[str, Any]:
    """Example long-running task that simulates work"""
    logger.info(f"Starting example task {task_id}")
    
    # Simulate work
    await asyncio.sleep(delay)
    
    # Simulate some processing
    result = {
        "task_id": task_id,
        "processed_at": datetime.utcnow().isoformat(),
        "computation_result": task_id * 2,
        "status": "completed"
    }
    
    logger.info(f"Completed example task {task_id}")
    return result


async def example_document_processing_task(document_id: str, processing_type: str) -> Dict[str, Any]:
    """Example document processing task"""
    logger.info(f"Processing document {document_id} with type {processing_type}")
    
    # Simulate document processing
    await asyncio.sleep(2)
    
    result = {
        "document_id": document_id,
        "processing_type": processing_type,
        "processed_at": datetime.utcnow().isoformat(),
        "extracted_data": {
            "title": f"Document {document_id}",
            "content_length": len(document_id) * 10,
            "metadata": {"type": processing_type}
        }
    }
    
    logger.info(f"Completed processing document {document_id}")
    return result


# Main function for testing
async def main():
    """Example usage of the JobService"""
    service = None
    try:
        # Initialize service
        service = JobService()
        await service.init_database()
        
        # Example 1: Create and run a simple job
        print("=== Example 1: Simple Job ===")
        job_data = JobCreate(
            job_type="example_task",
            initial_data={"description": "Test job"}
        )
        
        job = await service.create_job(job_data)
        print(f"Created job: {job.job_id}")
        
        # Run the job
        future = service.run_job_async(job.job_id, example_long_running_task, 1, 2)
        
        # Mark as started
        await service.start_job(job.job_id)
        
        # Wait for completion
        result = future.result()
        print(f"Job result: {result}")
        
        # Mark as completed
        await service.complete_job(job.job_id, {"result": result})
        
        # Example 2: Using the decorator
        print("\n=== Example 2: Decorator Job ===")
        
        @run_as_job("document_processing", document_id=uuid.uuid4())
        async def process_document():
            return await example_document_processing_task("DOC123", "OCR")
        
        result = await process_document()
        print(f"Decorator job result: {result}")
        
        # Example 3: Check job status
        print("\n=== Example 3: Job Status ===")
        all_jobs = await service.get_all_jobs()
        print(f"Total jobs: {len(all_jobs)}")
        
        for job in all_jobs:
            print(f"Job {job.job_id}: {job.job_type} - {job.status}")
            if job.result:
                print(f"  Result: {job.result}")
            if job.error_message:
                print(f"  Error: {job.error_message}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise
    finally:
        if service:
            await service.close()


if __name__ == "__main__":
    asyncio.run(main()) 