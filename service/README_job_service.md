# Job Service Framework

A comprehensive framework for running asynchronous jobs with database tracking, built on top of SQLAlchemy and ThreadPoolExecutor.

## Features

- **Database Tracking**: All jobs are tracked in a PostgreSQL database with status updates
- **Asynchronous Execution**: Uses ThreadPoolExecutor for non-blocking job execution
- **Status Management**: Tracks job lifecycle: scheduled → in_progress → done/failed
- **Error Handling**: Comprehensive error tracking and failure management
- **Decorator Support**: Easy-to-use decorator for automatic job tracking
- **Resource Management**: Automatic cleanup and connection management

## Database Schema

The framework uses the following database table structure:

```sql
CREATE TYPE job_status AS ENUM ('scheduled', 'in_progress', 'done', 'failed');

CREATE TABLE jobs (
    job_id        uuid       DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    document_id   uuid       REFERENCES documents ON DELETE CASCADE,
    job_type      varchar(50) NOT NULL,
    status        job_status DEFAULT 'scheduled'::job_status,
    created_at    timestamp  DEFAULT CURRENT_TIMESTAMP,
    started_at    timestamp,
    finished_at   timestamp,
    result        jsonb      DEFAULT '{}'::jsonb,
    error_message text,
    property_id   uuid       REFERENCES properties ON DELETE CASCADE
);
```

## Installation

1. Ensure you have the required dependencies:
   ```bash
   pip install sqlalchemy[asyncio] asyncpg pydantic python-dotenv
   ```

2. Set up your environment variables:
   ```bash
   # .env file
   DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
   ```

## Basic Usage

### 1. Manual Job Management

```python
from app.core.job_service import JobService, JobCreate
import asyncio

async def main():
    service = JobService()
    
    try:
        # Initialize database
        await service.init_database()
        
        # Create a job
        job_data = JobCreate(
            job_type="data_processing",
            document_id=uuid.uuid4(),
            initial_data={"description": "Process user data"}
        )
        
        job = await service.create_job(job_data)
        print(f"Created job: {job.job_id}")
        
        # Start the job
        await service.start_job(job.job_id)
        
        # Run your task
        result = await your_processing_function()
        
        # Mark as completed
        await service.complete_job(job.job_id, {"result": result})
        
    finally:
        await service.close()

# Run the example
asyncio.run(main())
```

### 2. Using ThreadPoolExecutor for Async Execution

```python
async def main():
    service = JobService()
    
    try:
        await service.init_database()
        
        # Create and start job
        job = await service.create_job(JobCreate(job_type="async_task"))
        await service.start_job(job.job_id)
        
        # Submit to thread pool
        future = service.run_job_async(
            job.job_id, 
            your_long_running_function, 
            arg1, arg2
        )
        
        # Wait for completion
        result = future.result()
        await service.complete_job(job.job_id, {"result": result})
        
    finally:
        await service.close()
```

### 3. Using the Decorator

```python
from app.core.job_service import run_as_job

@run_as_job("document_processing", document_id=uuid.uuid4())
async def process_document():
    # Your processing logic here
    result = await perform_ocr_processing()
    return result

# The decorator automatically handles job creation, tracking, and cleanup
result = await process_document()
```

## Job Status Lifecycle

1. **scheduled**: Job is created and ready to run
2. **in_progress**: Job has started execution
3. **done**: Job completed successfully
4. **failed**: Job encountered an error

## API Reference

### JobService Class

#### Methods

- `create_job(job_data: JobCreate) -> Job`: Create a new job
- `update_job_status(job_id: uuid.UUID, update_data: JobUpdate) -> Job`: Update job status
- `start_job(job_id: uuid.UUID)`: Mark job as started
- `complete_job(job_id: uuid.UUID, result: Dict[str, Any])`: Mark job as completed
- `fail_job(job_id: uuid.UUID, error_message: str)`: Mark job as failed
- `get_job(job_id: uuid.UUID) -> Optional[Job]`: Retrieve job by ID
- `get_jobs_by_status(status: str) -> List[Job]`: Get jobs by status
- `get_all_jobs() -> List[Job]`: Get all jobs
- `run_job_async(job_id: uuid.UUID, task_func: Callable, *args, **kwargs) -> Future`: Run job asynchronously
- `cancel_job(job_id: uuid.UUID) -> bool`: Cancel a running job
- `is_job_running(job_id: uuid.UUID) -> bool`: Check if job is running
- `close()`: Cleanup resources

### Models

#### JobCreate
- `job_type: str`: Type/category of the job
- `document_id: Optional[uuid.UUID]`: Associated document ID
- `property_id: Optional[uuid.UUID]`: Associated property ID
- `initial_data: Optional[Dict[str, Any]]`: Initial data for the job

#### JobUpdate
- `status: Optional[str]`: New job status
- `started_at: Optional[datetime]`: When job started
- `finished_at: Optional[datetime]`: When job finished
- `result: Optional[Dict[str, Any]]`: Job result data
- `error_message: Optional[str]`: Error message if failed

## Examples

### Document Processing Job

```python
@run_as_job("document_ocr", document_id=document_uuid)
async def process_document_ocr(document_path: str):
    # OCR processing logic
    ocr_result = await perform_ocr(document_path)
    
    # Extract text and metadata
    extracted_data = await extract_text(ocr_result)
    
    return {
        "text": extracted_data["text"],
        "confidence": extracted_data["confidence"],
        "pages": extracted_data["page_count"]
    }
```

### Data Analysis Job

```python
async def run_data_analysis():
    service = JobService()
    
    try:
        await service.init_database()
        
        # Create analysis job
        job = await service.create_job(JobCreate(
            job_type="data_analysis",
            initial_data={"dataset": "user_behavior", "records": 10000}
        ))
        
        # Start job
        await service.start_job(job.job_id)
        
        # Run analysis in background
        future = service.run_job_async(
            job.job_id,
            perform_data_analysis,
            "user_behavior",
            10000
        )
        
        # Wait for completion
        result = future.result()
        await service.complete_job(job.job_id, {"analysis": result})
        
        return result
        
    finally:
        await service.close()
```

### Batch Job Processing

```python
async def process_batch_jobs(job_list: List[Dict[str, Any]]):
    service = JobService()
    
    try:
        await service.init_database()
        
        jobs = []
        for job_data in job_list:
            job = await service.create_job(JobCreate(**job_data))
            jobs.append(job)
        
        # Start all jobs
        futures = []
        for job in jobs:
            await service.start_job(job.job_id)
            future = service.run_job_async(
                job.job_id,
                process_single_job,
                job.job_id
            )
            futures.append((job.job_id, future))
        
        # Wait for all jobs to complete
        results = []
        for job_id, future in futures:
            try:
                result = future.result()
                await service.complete_job(job_id, {"result": result})
                results.append(result)
            except Exception as e:
                await service.fail_job(job_id, str(e))
        
        return results
        
    finally:
        await service.close()
```

## Error Handling

The framework provides comprehensive error handling:

```python
try:
    # Your job logic
    result = await your_function()
    await service.complete_job(job_id, {"result": result})
    
except Exception as e:
    # Log the error
    logger.error(f"Job {job_id} failed: {e}")
    
    # Mark job as failed with error details
    await service.fail_job(job_id, str(e))
    
    # Re-raise if needed
    raise
```

## Best Practices

1. **Always close the service**: Use try-finally blocks to ensure cleanup
2. **Handle errors gracefully**: Update job status to 'failed' when errors occur
3. **Use appropriate job types**: Categorize jobs for better tracking
4. **Monitor job status**: Regularly check job status for long-running operations
5. **Resource management**: Be mindful of ThreadPoolExecutor worker limits

## Testing

Run the test script to verify functionality:

```bash
cd service
python test_job_service.py
```

## Running Examples

Execute the comprehensive examples:

```bash
cd service
python examples/job_example.py
```

## Configuration

The framework automatically handles:
- Database connection pooling
- SSL configuration for Neon PostgreSQL
- Asyncpg compatibility
- Connection recycling
- Resource cleanup

## Dependencies

- Python 3.8+
- SQLAlchemy 2.0+
- asyncpg
- Pydantic 2.0+
- python-dotenv

## License

This framework is part of the Hackathon-Aug-25-Team5 project. 