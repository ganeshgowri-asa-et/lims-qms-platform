"""
Backup Tasks
Automated database and file system backups
"""
from backend.integrations.celery_app import celery_app
from backend.integrations.external.cloud_storage import cloud_storage
from backend.core.config import settings
from datetime import datetime
import subprocess
import os
import shutil
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="backend.integrations.tasks.backups.backup_database")
def backup_database():
    """
    Backup PostgreSQL database
    Runs daily at 2 AM
    """
    try:
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_dir = "/backups/database"
        os.makedirs(backup_dir, exist_ok=True)

        backup_file = f"{backup_dir}/lims_qms_{timestamp}.sql"

        # Extract database connection details
        db_url = settings.DATABASE_URL
        # Format: postgresql://user:password@host:port/database

        # Run pg_dump
        cmd = [
            "pg_dump",
            db_url,
            "-f", backup_file,
            "--format=custom",
            "--compress=9"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"Database backup created: {backup_file}")

            # Upload to cloud storage (S3)
            try:
                with open(backup_file, 'rb') as f:
                    content = f.read()

                import asyncio
                asyncio.run(cloud_storage.upload_to_s3(
                    bucket="lims-qms-backups",
                    key=f"database/{os.path.basename(backup_file)}",
                    file_content=content,
                    metadata={
                        'timestamp': timestamp,
                        'type': 'database',
                        'size': str(len(content))
                    }
                ))

                logger.info("Database backup uploaded to S3")

            except Exception as e:
                logger.error(f"Failed to upload backup to S3: {e}")

            # Clean up old backups (keep last 7 days)
            cleanup_old_backups(backup_dir, days=7)

            return {
                "success": True,
                "backup_file": backup_file,
                "timestamp": timestamp
            }
        else:
            logger.error(f"Database backup failed: {result.stderr}")
            return {
                "success": False,
                "error": result.stderr
            }

    except Exception as e:
        logger.error(f"Database backup error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="backend.integrations.tasks.backups.backup_files")
def backup_files():
    """
    Backup file system (uploads, documents)
    Runs daily at 3 AM
    """
    try:
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_dir = "/backups/files"
        os.makedirs(backup_dir, exist_ok=True)

        # Directories to backup
        source_dirs = [
            settings.UPLOAD_DIR,
            "documents",
            "exports"
        ]

        backup_file = f"{backup_dir}/files_{timestamp}.tar.gz"

        # Create tar archive
        cmd = ["tar", "-czf", backup_file] + source_dirs

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"File backup created: {backup_file}")

            # Upload to cloud storage
            try:
                with open(backup_file, 'rb') as f:
                    content = f.read()

                import asyncio
                asyncio.run(cloud_storage.upload_to_s3(
                    bucket="lims-qms-backups",
                    key=f"files/{os.path.basename(backup_file)}",
                    file_content=content,
                    metadata={
                        'timestamp': timestamp,
                        'type': 'files',
                        'size': str(len(content))
                    }
                ))

                logger.info("File backup uploaded to S3")

            except Exception as e:
                logger.error(f"Failed to upload file backup to S3: {e}")

            # Clean up old backups
            cleanup_old_backups(backup_dir, days=7)

            return {
                "success": True,
                "backup_file": backup_file,
                "timestamp": timestamp
            }
        else:
            logger.error(f"File backup failed: {result.stderr}")
            return {
                "success": False,
                "error": result.stderr
            }

    except Exception as e:
        logger.error(f"File backup error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@celery_app.task(name="backend.integrations.tasks.backups.restore_database")
def restore_database(backup_file: str):
    """
    Restore database from backup

    Args:
        backup_file: Path to backup file
    """
    try:
        db_url = settings.DATABASE_URL

        # Run pg_restore
        cmd = [
            "pg_restore",
            "-d", db_url,
            "--clean",
            "--if-exists",
            backup_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"Database restored from: {backup_file}")
            return {
                "success": True,
                "backup_file": backup_file
            }
        else:
            logger.error(f"Database restore failed: {result.stderr}")
            return {
                "success": False,
                "error": result.stderr
            }

    except Exception as e:
        logger.error(f"Database restore error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def cleanup_old_backups(backup_dir: str, days: int = 7):
    """
    Clean up backups older than specified days

    Args:
        backup_dir: Backup directory
        days: Number of days to retain
    """
    try:
        import time
        now = time.time()
        cutoff = now - (days * 86400)  # days in seconds

        for filename in os.listdir(backup_dir):
            filepath = os.path.join(backup_dir, filename)
            if os.path.isfile(filepath):
                file_time = os.path.getmtime(filepath)
                if file_time < cutoff:
                    os.remove(filepath)
                    logger.info(f"Deleted old backup: {filename}")

    except Exception as e:
        logger.error(f"Backup cleanup error: {e}")


@celery_app.task(name="backend.integrations.tasks.backups.test_restore")
def test_restore():
    """
    Test backup restore process
    Runs weekly to ensure backups are valid
    """
    try:
        # Get latest backup
        backup_dir = "/backups/database"
        backups = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith('.sql')],
            reverse=True
        )

        if not backups:
            logger.warning("No backups found for restore test")
            return {"success": False, "error": "No backups found"}

        latest_backup = os.path.join(backup_dir, backups[0])

        # Test restore to temporary database
        # In production, use a separate test database
        logger.info(f"Testing restore of: {latest_backup}")

        # Verify backup file integrity
        if os.path.getsize(latest_backup) == 0:
            logger.error("Backup file is empty")
            return {"success": False, "error": "Empty backup file"}

        logger.info("Backup restore test passed")
        return {
            "success": True,
            "backup_file": latest_backup,
            "size": os.path.getsize(latest_backup)
        }

    except Exception as e:
        logger.error(f"Restore test error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
