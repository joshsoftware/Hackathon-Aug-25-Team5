#!/usr/bin/env python3
"""
Simple script to verify that job entries exist in the database.
Run this after creating jobs to confirm they were saved.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the job service
from app.core.job_service import JobService


async def verify_database_entries():
    """Verify that job entries exist in the database"""
    print("Verifying database entries...")
    
    # Check environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables!")
        print("Please set DATABASE_URL in your .env file")
        return
    
    service = None
    try:
        service = JobService()
        await service.init_database()
        
        # Get all jobs
        all_jobs = await service.get_all_jobs()
        
        if not all_jobs:
            print("❌ No jobs found in database!")
            print("This could mean:")
            print("  1. No jobs have been created yet")
            print("  2. Database connection issues")
            print("  3. Table doesn't exist")
            return
        
        print(f"✅ Found {len(all_jobs)} job(s) in database")
        print("\nJob Details:")
        print("-" * 80)
        
        # Group jobs by status
        status_counts = {}
        for job in all_jobs:
            status = job.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Display summary
        print("Status Summary:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        print("\nDetailed Job Information:")
        print("-" * 80)
        
        for i, job in enumerate(all_jobs, 1):
            print(f"\nJob {i}:")
            print(f"  ID: {job.job_id}")
            print(f"  Type: {job.job_type}")
            print(f"  Status: {job.status}")
            print(f"  Created: {job.created_at}")
            
            if job.started_at:
                print(f"  Started: {job.started_at}")
            if job.finished_at:
                print(f"  Finished: {job.finished_at}")
            if job.document_id:
                print(f"  Document ID: {job.document_id}")
            if job.property_id:
                print(f"  Property ID: {job.property_id}")
            if job.result:
                print(f"  Result: {job.result}")
            if job.error_message:
                print(f"  Error: {job.error_message}")
        
        # Test database operations
        print("\n" + "="*80)
        print("Testing Database Operations:")
        print("="*80)
        
        # Test getting jobs by status
        for status in ['scheduled', 'in_progress', 'done', 'failed']:
            try:
                jobs_by_status = await service.get_jobs_by_status(status)
                print(f"  Jobs with status '{status}': {len(jobs_by_status)}")
            except Exception as e:
                print(f"  Error getting jobs with status '{status}': {e}")
        
        print("\n✅ Database verification completed successfully!")
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if service:
            await service.close()


async def main():
    """Main function"""
    print("JobService Database Entry Verification")
    print("="*60)
    
    await verify_database_entries()


if __name__ == "__main__":
    asyncio.run(main()) 