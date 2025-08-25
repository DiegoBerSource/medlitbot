#!/usr/bin/env python3
"""
Simple monitoring script to check for stuck training jobs
Run this periodically (e.g., with cron) to auto-cleanup stuck jobs
"""
import sqlite3
import os
from datetime import datetime, timedelta
import sys


def check_stuck_jobs(cleanup=False, timeout_hours=2):
    """
    Check for stuck training jobs and optionally clean them up
    """
    db_path = 'db.sqlite3'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find stuck jobs
    timeout_threshold = (datetime.now() - timedelta(hours=timeout_hours)).isoformat()
    
    cursor.execute("""
        SELECT 
            tj.id, tj.status, tj.progress_percentage, tj.created_at,
            tj.celery_task_id, m.name, m.id as model_id
        FROM classification_trainingjob tj
        JOIN classification_mlmodel m ON tj.model_id = m.id
        WHERE tj.status IN ('running', 'pending')
        AND tj.created_at < ?
    """, (timeout_threshold,))
    
    stuck_jobs = cursor.fetchall()
    
    if not stuck_jobs:
        print(f"✅ No stuck training jobs found (timeout: {timeout_hours}h)")
        conn.close()
        return True
    
    print(f"🚨 Found {len(stuck_jobs)} stuck training jobs:")
    for job in stuck_jobs:
        job_id, status, progress, created_at, celery_id, model_name, model_id = job
        age_hours = (datetime.now() - datetime.fromisoformat(created_at)).total_seconds() / 3600
        print(f"  - Job {job_id}: {model_name} ({status}, {progress}%, {age_hours:.1f}h old)")
    
    if not cleanup:
        print("\n💡 Run with --cleanup to fix these automatically")
        conn.close()
        return len(stuck_jobs) == 0
    
    # Cleanup stuck jobs
    fixed_count = 0
    current_time = datetime.now().isoformat()
    
    for job in stuck_jobs:
        job_id, _, _, _, _, model_name, model_id = job
        
        try:
            # Update training job status
            cursor.execute("""
                UPDATE classification_trainingjob 
                SET status = 'failed',
                    error_message = 'Training job was stuck and cleaned up automatically',
                    completed_at = ?
                WHERE id = ?
            """, (current_time, job_id))
            
            # Update model status
            cursor.execute("""
                UPDATE classification_mlmodel 
                SET status = 'failed'
                WHERE id = ?
            """, (model_id,))
            
            print(f"✅ Fixed job {job_id}: {model_name}")
            fixed_count += 1
            
        except Exception as e:
            print(f"❌ Failed to fix job {job_id}: {e}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Fixed {fixed_count} stuck training jobs!")
    return fixed_count > 0


def main():
    """
    Main function - can be used as a CLI tool
    """
    cleanup = '--cleanup' in sys.argv
    force_cleanup = '--force' in sys.argv
    
    # Parse timeout argument
    timeout_hours = 2
    for arg in sys.argv:
        if arg.startswith('--timeout='):
            timeout_hours = int(arg.split('=')[1])
    
    if force_cleanup:
        cleanup = True
    
    print(f"🔍 Monitoring training jobs (timeout: {timeout_hours}h, cleanup: {cleanup})")
    
    success = check_stuck_jobs(cleanup=cleanup, timeout_hours=timeout_hours)
    
    if not success and not cleanup:
        print("\n⚠️  Stuck jobs detected but not cleaned up")
        sys.exit(1)


if __name__ == "__main__":
    main()
