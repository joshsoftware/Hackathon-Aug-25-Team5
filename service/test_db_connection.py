#!/usr/bin/env python3
"""
Database connection test script for JobService.
This script will actually connect to the database and test job creation.
"""

import asyncio
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the job service
from app.core.job_service import JobService, JobCreate


async def test_database_connection():
    """Test basic database connectivity"""
    print("Testing database connection...")
    
    try:
        service = JobService()
        print("✓ JobService created successfully")
        
        # Test database initialization
        await service.init_database()
        print("✓ Database tables initialized successfully")
        
        await service.close()
        print("✓ Database connection closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


async def test_job_creation():
    """Test actual job creation in database"""
    print("\nTesting job creation in database...")
    
    service = None
    try:
        service = JobService()
        await service.init_database()
        
        # Create a test job
        job_data = JobCreate(
            job_type="test_job",
            document_id=uuid.uuid4(),
            initial_data={
                "test": True,
                "created_at": datetime.utcnow().isoformat(),
                "description": "Test job for database verification"
            }
        )
        
        print(f"Creating job with data: {job_data}")
        
        # Create the job
        job = await service.create_job(job_data)
        print(f"✓ Job created successfully!")
        print(f"  Job ID: {job.job_id}")
        print(f"  Job Type: {job.job_type}")
        print(f"  Status: {job.status}")
        print(f"  Created At: {job.created_at}")
        
        # Verify the job exists in database
        retrieved_job = await service.get_job(job.job_id)
        if retrieved_job:
            print(f"✓ Job retrieved from database successfully!")
            print(f"  Retrieved Job ID: {retrieved_job.job_id}")
            print(f"  Retrieved Status: {retrieved_job.status}")
        else:
            print("✗ Failed to retrieve job from database")
            return False
        
        # Test job status update
        print("\nTesting job status update...")
        await service.start_job(job.job_id)
        
        updated_job = await service.get_job(job.job_id)
        print(f"✓ Job status updated to: {updated_job.status}")
        print(f"  Started At: {updated_job.started_at}")
        
        # Test job completion
        print("\nTesting job completion...")
        result_data = {
            "test_result": "success",
            "processed_at": datetime.utcnow().isoformat(),
            "computation_time": "0.5s"
        }
        
        await service.complete_job(job.job_id, result_data)
        
        final_job = await service.get_job(job.job_id)
        print(f"✓ Job completed successfully!")
        print(f"  Final Status: {final_job.status}")
        print(f"  Finished At: {final_job.finished_at}")
        print(f"  Result: {final_job.result}")
        
        return True
        
    except Exception as e:
        print(f"✗ Job creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if service:
            await service.close()


async def test_multiple_jobs():
    """Test creating multiple jobs"""
    print("\nTesting multiple job creation...")
    
    service = None
    try:
        service = JobService()
        await service.init_database()
        
        # Create multiple test jobs
        job_types = ["ocr_processing", "data_analysis", "file_upload", "validation"]
        created_jobs = []
        
        for i, job_type in enumerate(job_types):
            job_data = JobCreate(
                job_type=job_type,
                document_id=uuid.uuid4(),
                initial_data={
                    "batch_id": f"batch_{i+1}",
                    "created_at": datetime.utcnow().isoformat()
                }
            )
            
            job = await service.create_job(job_data)
            created_jobs.append(job)
            print(f"✓ Created job {i+1}: {job.job_id} ({job_type})")
        
        # Verify all jobs exist
        all_jobs = await service.get_all_jobs()
        print(f"\nTotal jobs in database: {len(all_jobs)}")
        
        # Check jobs by status
        scheduled_jobs = await service.get_jobs_by_status("scheduled")
        print(f"Scheduled jobs: {len(scheduled_jobs)}")
        
        # Display job summary
        print("\nJob Summary:")
        for job in all_jobs:
            print(f"  {job.job_id}: {job.job_type} - {job.status}")
        
        return True
        
    except Exception as e:
        print(f"✗ Multiple job creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if service:
            await service.close()


async def test_job_failure():
    """Test job failure handling"""
    print("\nTesting job failure handling...")
    
    service = None
    try:
        service = JobService()
        await service.init_database()
        
        # Create a job that will fail
        job_data = JobCreate(
            job_type="failing_job",
            initial_data={"description": "This job will fail for testing"}
        )
        
        job = await service.create_job(job_data)
        print(f"✓ Created failing job: {job.job_id}")
        
        # Start the job
        await service.start_job(job.job_id)
        print(f"✓ Started failing job")
        
        # Simulate failure
        error_message = "Simulated error: Database connection timeout"
        await service.fail_job(job.job_id, error_message)
        print(f"✓ Marked job as failed")
        
        # Verify failure status
        failed_job = await service.get_job(job.job_id)
        print(f"✓ Job failure recorded successfully!")
        print(f"  Status: {failed_job.status}")
        print(f"  Error Message: {failed_job.error_message}")
        print(f"  Finished At: {failed_job.finished_at}")
        
        return True
        
    except Exception as e:
        print(f"✗ Job failure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if service:
            await service.close()


async def main():
    """Run all database tests"""
    print("JobService Database Connection Tests")
    print("="*60)
    
    # Check environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables!")
        print("Please set DATABASE_URL in your .env file")
        return
    
    print(f"Database URL: {database_url[:50]}...")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Job Creation", test_job_creation),
        ("Multiple Jobs", test_multiple_jobs),
        ("Job Failure", test_job_failure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "="*60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All database tests passed! Job entries are being created successfully.")
    else:
        print("❌ Some database tests failed. Check the output above for details.")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main()) 