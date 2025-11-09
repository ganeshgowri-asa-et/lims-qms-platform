"""
Monitoring Tasks
System health checks, performance metrics, error tracking
"""
from backend.integrations.celery_app import celery_app
from backend.integrations.events import event_bus, Event, EventType
from backend.core.config import settings
from datetime import datetime
import psutil
import httpx
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="backend.integrations.tasks.monitoring.system_health_check")
def system_health_check():
    """
    Perform system health check
    Runs every 5 minutes
    """
    try:
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "checks": {}
        }

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        health_status["checks"]["cpu"] = {
            "status": "ok" if cpu_percent < 80 else "warning",
            "usage_percent": cpu_percent
        }

        # Memory usage
        memory = psutil.virtual_memory()
        health_status["checks"]["memory"] = {
            "status": "ok" if memory.percent < 80 else "warning",
            "usage_percent": memory.percent,
            "available_gb": round(memory.available / (1024**3), 2)
        }

        # Disk usage
        disk = psutil.disk_usage('/')
        health_status["checks"]["disk"] = {
            "status": "ok" if disk.percent < 80 else "warning",
            "usage_percent": disk.percent,
            "free_gb": round(disk.free / (1024**3), 2)
        }

        # Database connection
        try:
            import asyncio
            from backend.core.database import SessionLocal

            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()

            health_status["checks"]["database"] = {
                "status": "ok",
                "connected": True
            }
        except Exception as e:
            health_status["checks"]["database"] = {
                "status": "error",
                "connected": False,
                "error": str(e)
            }
            health_status["status"] = "degraded"

        # Redis connection
        try:
            import asyncio
            import redis
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            r.close()

            health_status["checks"]["redis"] = {
                "status": "ok",
                "connected": True
            }
        except Exception as e:
            health_status["checks"]["redis"] = {
                "status": "error",
                "connected": False,
                "error": str(e)
            }
            health_status["status"] = "degraded"

        # API endpoint check
        try:
            import asyncio
            async def check_api():
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://localhost:8000/health")
                    return response.status_code == 200

            api_healthy = asyncio.run(check_api())

            health_status["checks"]["api"] = {
                "status": "ok" if api_healthy else "error",
                "responsive": api_healthy
            }
        except Exception as e:
            health_status["checks"]["api"] = {
                "status": "error",
                "responsive": False,
                "error": str(e)
            }

        # Determine overall status
        if any(check["status"] == "error" for check in health_status["checks"].values()):
            health_status["status"] = "unhealthy"
        elif any(check["status"] == "warning" for check in health_status["checks"].values()):
            health_status["status"] = "degraded"

        logger.info(f"Health check: {health_status['status']}")

        # Publish event if unhealthy
        if health_status["status"] != "healthy":
            import asyncio
            asyncio.run(event_bus.publish(Event(
                type=EventType.SYSTEM_ERROR,
                source="health_check",
                data=health_status
            )))

        return health_status

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@celery_app.task(name="backend.integrations.tasks.monitoring.collect_performance_metrics")
def collect_performance_metrics():
    """
    Collect performance metrics
    Runs every hour
    """
    try:
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {},
            "application": {}
        }

        # System metrics
        metrics["system"]["cpu"] = {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(),
            "freq": psutil.cpu_freq().current if psutil.cpu_freq() else None
        }

        metrics["system"]["memory"] = {
            "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "percent": psutil.virtual_memory().percent
        }

        metrics["system"]["disk"] = {
            "total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
            "free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
            "percent": psutil.disk_usage('/').percent
        }

        # Network I/O
        net_io = psutil.net_io_counters()
        metrics["system"]["network"] = {
            "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
            "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2)
        }

        # Process metrics
        process = psutil.Process()
        metrics["application"]["process"] = {
            "cpu_percent": process.cpu_percent(),
            "memory_mb": round(process.memory_info().rss / (1024**2), 2),
            "threads": process.num_threads(),
            "open_files": len(process.open_files())
        }

        # Application-specific metrics
        # Would query database for API request counts, response times, etc.
        metrics["application"]["api"] = {
            "total_requests": 0,  # Placeholder
            "avg_response_time_ms": 0,  # Placeholder
            "error_rate": 0  # Placeholder
        }

        logger.info("Performance metrics collected")
        return metrics

    except Exception as e:
        logger.error(f"Metrics collection error: {e}")
        return {
            "error": str(e)
        }


@celery_app.task(name="backend.integrations.tasks.monitoring.cleanup_logs")
def cleanup_logs():
    """
    Clean up old log files
    Runs weekly
    """
    try:
        import os
        import time

        log_dir = "logs"
        if not os.path.exists(log_dir):
            return {"cleaned": 0}

        # Delete logs older than 30 days
        now = time.time()
        cutoff = now - (30 * 86400)

        cleaned = 0
        for filename in os.listdir(log_dir):
            filepath = os.path.join(log_dir, filename)
            if os.path.isfile(filepath):
                file_time = os.path.getmtime(filepath)
                if file_time < cutoff:
                    os.remove(filepath)
                    cleaned += 1

        logger.info(f"Cleaned up {cleaned} old log files")
        return {"cleaned": cleaned}

    except Exception as e:
        logger.error(f"Log cleanup error: {e}")
        return {"error": str(e)}


@celery_app.task(name="backend.integrations.tasks.monitoring.monitor_errors")
def monitor_errors():
    """
    Monitor and report application errors
    Runs every hour
    """
    try:
        # Query error logs or error tracking service
        # Placeholder for actual error monitoring
        errors = {
            "timestamp": datetime.utcnow().isoformat(),
            "period": "last_hour",
            "total_errors": 0,
            "critical_errors": 0,
            "error_types": {}
        }

        # In production, integrate with Sentry or similar service
        logger.info("Error monitoring completed")
        return errors

    except Exception as e:
        logger.error(f"Error monitoring failed: {e}")
        return {"error": str(e)}
