#!/usr/bin/env python3
"""
Example script demonstrating the JobService framework usage.
This shows different ways to create, run, and monitor asynchronous jobs.
"""

import asyncio
import uuid
import time
from datetime import datetime
from typing import Dict, Any

# Import the job service
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.job_service import JobService, JobCreate, run_as_job


# Example job functions
async def simple_calculation_task(number: int, delay: int = 2) -> Dict[str, Any]:
    """Simple calculation task that takes some time"""
    print(f"Starting calculation for number {number}")
    
    # Simulate work
    await asyncio.sleep(delay)
    
    result = {
        "input_number": number,
        "square": number ** 2,
        "cube": number ** 3,
        "processed_at": datetime.utcnow().isoformat()
    }
    
    print(f"Completed calculation for number {number}")
    return result


async def document_ocr_task(document_id: str, pages: int = 5) -> Dict[str, Any]:
    """Simulate OCR processing of a document"""
    print(f"Starting OCR processing for document {document_id}")
    
    # Simulate processing each page
    for page in range(1, pages + 1):
        print(f"  Processing page {page}/{pages}")
        await asyncio.sleep(1)  # Simulate page processing time
    
    result = {
        "document_id": document_id,
        "pages_processed": pages,
        "ocr_text": f"Sample OCR text from {document_id}",
        "confidence_score": 0.95,
        "processed_at": datetime.utcnow().isoformat()
    }
    
    print(f"Completed OCR processing for document {document_id}")
    return result


async def data_analysis_task(dataset_name: str, records: int = 1000) -> Dict[str, Any]:
    """Simulate data analysis task"""
    print(f"Starting data analysis for dataset {dataset_name}")
    
    # Simulate data processing
    await asyncio.sleep(3)
    
    result = {
        "dataset": dataset_name,
        "records_analyzed": records,
        "insights": [
            "Pattern A detected in 45% of records",
            "Anomaly found in record 234",
            "Correlation coefficient: 0.78"
        ],
        "processing_time_seconds": 3,
        "processed_at": datetime.utcnow().isoformat()
    }
    
    print(f"Completed data analysis for dataset {dataset_name}")
    return result


# Example using the decorator
@run_as_job("decorator_example", document_id=uuid.uuid4())
async def decorated_task():
    """Task that automatically gets tracked using the decorator"""
    print("Running decorated task...")
    await asyncio.sleep(2)
    return {"message": "Decorated task completed successfully"}


async def example_1_manual_job_management():
    """Example 1: Manual job creation and management"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Manual Job Management")
    print("="*60)
    
    service = JobService()
    
    try:
        # Initialize database
        await service.init_database()
        
        # Create a job
        job_data = JobCreate(
            job_type="calculation_task",
            initial_data={"description": "Calculate squares and cubes"}
        )
        
        job = await service.create_job(job_data)
        print(f"Created job: {job.job_id}")
        print(f"Job status: {job.status}")
        
        # Start the job
        await service.start_job(job.job_id)
        print(f"Job started at: {job.started_at}")
        
        # Run the actual task
        print("Running calculation task...")
        result = await simple_calculation_task(5, delay=3)
        
        # Mark job as completed
        await service.complete_job(job.job_id, result)
        print(f"Job completed successfully!")
        
        # Retrieve and display the final job status
        final_job = await service.get_job(job.job_id)
        print(f"Final job status: {final_job.status}")
        print(f"Job result: {final_job.result}")
        
    except Exception as e:
        print(f"Error in manual job management: {e}")
    finally:
        await service.close()


async def example_2_async_job_execution():
    """Example 2: Using ThreadPoolExecutor for async execution"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Async Job Execution with ThreadPoolExecutor")
    print("="*60)
    
    service = JobService()
    
    try:
        await service.init_database()
        
        # Create multiple jobs
        jobs = []
        for i in range(3):
            job_data = JobCreate(
                job_type="async_calculation",
                initial_data={"task_number": i + 1}
            )
            job = await service.create_job(job_data)
            jobs.append(job)
            print(f"Created job {i + 1}: {job.job_id}")
        
        # Start all jobs asynchronously
        futures = []
        for job in jobs:
            await service.start_job(job.job_id)
            future = service.run_job_async(
                job.job_id, 
                lambda x: asyncio.run(simple_calculation_task(x, 1)), 
                jobs.index(job) + 1
            )
            futures.append((job.job_id, future))
        
        print("All jobs started. Waiting for completion...")
        
        # Wait for all jobs to complete
        for job_id, future in futures:
            try:
                result = future.result(timeout=10)  # 10 second timeout
                await service.complete_job(job_id, result)
                print(f"Job {job_id} completed with result: {result}")
            except Exception as e:
                await service.fail_job(job_id, str(e))
                print(f"Job {job_id} failed with error: {e}")
        
        # Display final status
        all_jobs = await service.get_all_jobs()
        print(f"\nFinal job statuses:")
        for job in all_jobs:
            print(f"  {job.job_id}: {job.status}")
            
    except Exception as e:
        print(f"Error in async job execution: {e}")
    finally:
        await service.close()


async def example_3_decorator_usage():
    """Example 3: Using the @run_as_job decorator"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Decorator-based Job Tracking")
    print("="*60)
    
    try:
        # The decorator automatically handles job creation, tracking, and cleanup
        result = await decorated_task()
        print(f"Decorated task result: {result}")
        
        # Check if the job was created in the database
        service = JobService()
        await service.init_database()
        
        # Find the job by type
        jobs = await service.get_jobs_by_status("done")
        decorator_jobs = [j for j in jobs if j.job_type == "decorator_example"]
        
        if decorator_jobs:
            job = decorator_jobs[0]
            print(f"Decorator job found: {job.job_id}")
            print(f"Status: {job.status}")
            print(f"Result: {job.result}")
        
        await service.close()
        
    except Exception as e:
        print(f"Error in decorator usage: {e}")


async def example_4_error_handling():
    """Example 4: Error handling and job failure tracking"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Error Handling and Job Failure")
    print("="*60)
    
    service = JobService()
    
    try:
        await service.init_database()
        
        # Create a job that will fail
        job_data = JobCreate(
            job_type="failing_task",
            initial_data={"description": "This task will fail"}
        )
        
        job = await service.create_job(job_data)
        print(f"Created job: {job.job_id}")
        
        # Start the job
        await service.start_job(job.job_id)
        
        # Simulate a failing task
        try:
            print("Running failing task...")
            await asyncio.sleep(1)
            raise ValueError("Simulated error: Task failed intentionally")
        except Exception as e:
            await service.fail_job(job.job_id, str(e))
            print(f"Job marked as failed: {e}")
        
        # Check the final job status
        final_job = await service.get_job(job.job_id)
        print(f"Final job status: {final_job.status}")
        print(f"Error message: {final_job.error_message}")
        print(f"Finished at: {final_job.finished_at}")
        
    except Exception as e:
        print(f"Error in error handling example: {e}")
    finally:
        await service.close()


async def example_5_job_monitoring():
    """Example 5: Job monitoring and status checking"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Job Monitoring and Status Checking")
    print("="*60)
    
    service = JobService()
    
    try:
        await service.init_database()
        
        # Create a long-running job
        job_data = JobCreate(
            job_type="long_running_task",
            initial_data={"description": "Long running data analysis"}
        )
        
        job = await service.create_job(job_data)
        print(f"Created long-running job: {job.job_id}")
        
        # Start the job
        await service.start_job(job.job_id)
        
        # Start the task in background
        future = service.run_job_async(
            job.job_id,
            lambda: asyncio.run(data_analysis_task("large_dataset", 5000))
        )
        
        # Monitor the job status
        print("Monitoring job status...")
        for i in range(5):
            current_job = await service.get_job(job.job_id)
            print(f"  Check {i + 1}: Status = {current_job.status}")
            
            if service.is_job_running(job.job_id):
                print(f"    Job is still running...")
            else:
                print(f"    Job has finished")
                break
                
            await asyncio.sleep(1)
        
        # Wait for completion
        if not future.done():
            print("Job still running, waiting for completion...")
            result = future.result(timeout=10)
            await service.complete_job(job.job_id, result)
            print(f"Job completed with result: {result}")
        
        # Display final statistics
        all_jobs = await service.get_all_jobs()
        status_counts = {}
        for job in all_jobs:
            status = job.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\nJob Statistics:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
            
    except Exception as e:
        print(f"Error in job monitoring: {e}")
    finally:
        await service.close()


async def main():
    """Run all examples"""
    print("JobService Framework Examples")
    print("="*60)
    
    try:
        # Run all examples
        await example_1_manual_job_management()
        await example_2_async_job_execution()
        await example_3_decorator_usage()
        await example_4_error_handling()
        await example_5_job_monitoring()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"Error running examples: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 