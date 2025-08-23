# Testing Guide: Verify Database Entry Creation

This guide will help you verify that the JobService framework is successfully creating database entries.

## Prerequisites

1. **Environment Setup**: Ensure you have a `.env` file with your `DATABASE_URL`
2. **Database Access**: Make sure your database is accessible
3. **Dependencies**: Install required packages

## Step 1: Check Environment Variables

First, verify your environment is set up correctly:

```bash
cd service
cat .env
```

You should see something like:
```
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
```

## Step 2: Run Basic Tests

Start with the basic functionality tests:

```bash
python test_job_service.py
```

This will test the models and basic structure without database connection.

## Step 3: Test Database Connection

Run the database connection test:

```bash
python test_db_connection.py
```

**Expected Output:**
```
JobService Database Connection Tests
============================================================
Database URL: postgresql://username:password@host:port/database...
==================================================== Database Connection ====================================================
Testing database connection...
✓ JobService created successfully
✓ Database tables initialized successfully
✓ Database connection closed successfully
✅ Database Connection PASSED
```

## Step 4: Test Job Creation

If the connection test passes, the job creation test will run automatically and should show:

```
==================================================== Job Creation ====================================================
Testing job creation in database...
Creating job with data: job_type='test_job' document_id=UUID('...') ...
✓ Job created successfully!
  Job ID: [UUID]
  Job Type: test_job
  Status: scheduled
  Created At: [timestamp]
✓ Job retrieved from database successfully!
```

## Step 5: Verify Database Entries

After running the tests, verify that entries were actually created:

```bash
python verify_db_entries.py
```

**Expected Output:**
```
✅ Found X job(s) in database

Job Details:
--------------------------------------------------------------------------------
Job 1:
  ID: [UUID]
  Type: test_job
  Status: done
  Created: [timestamp]
  Started: [timestamp]
  Finished: [timestamp]
  Result: {'test_result': 'success', ...}
```

## Step 6: Manual Verification (Optional)

You can also manually check your database:

```sql
-- Connect to your database and run:
SELECT * FROM jobs ORDER BY created_at DESC LIMIT 5;
```

## Troubleshooting

### Issue: "DATABASE_URL not found"
**Solution**: Create or update your `.env` file in the `service/` directory

### Issue: "Database connection failed"
**Solutions**:
1. Check if your database is running
2. Verify the connection string format
3. Ensure network access to the database

### Issue: "No jobs found in database"
**Solutions**:
1. Run the tests first to create jobs
2. Check if the `jobs` table exists
3. Verify database permissions

### Issue: "Table doesn't exist"
**Solution**: The `init_database()` method should create tables automatically. Check for errors in the initialization.

## Expected Database Schema

After successful initialization, you should have:

```sql
-- Check if the enum type exists
SELECT typname FROM pg_type WHERE typname = 'job_status';

-- Check if the table exists
SELECT tablename FROM pg_tables WHERE tablename = 'jobs';

-- Check table structure
\d jobs
```

## Success Indicators

✅ **Database Connection**: Service connects without errors  
✅ **Table Creation**: `jobs` table is created automatically  
✅ **Job Creation**: Jobs are inserted with proper UUIDs  
✅ **Status Updates**: Job status changes are recorded  
✅ **Data Retrieval**: Jobs can be queried by various criteria  

## Next Steps

Once database entry creation is verified:

1. **Integration**: Use the JobService in your existing applications
2. **Monitoring**: Set up job status monitoring
3. **Scaling**: Adjust ThreadPoolExecutor worker count as needed
4. **Customization**: Extend job types and result structures

## Support

If you encounter issues:

1. Check the logs for detailed error messages
2. Verify database connectivity independently
3. Ensure all dependencies are installed
4. Check database user permissions 