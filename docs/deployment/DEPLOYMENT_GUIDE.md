# LIMS-QMS Platform - Deployment Guide

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Database Setup](#database-setup)
5. [Environment Configuration](#environment-configuration)
6. [Troubleshooting](#troubleshooting)

## Local Development Setup

### Prerequisites
- Python 3.11 or higher
- PostgreSQL 15 or higher
- Git
- Virtual environment tool (venv or conda)

### Step-by-Step Installation

1. **Clone the Repository**
```bash
git clone https://github.com/ganeshgowri-asa-et/lims-qms-platform.git
cd lims-qms-platform
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Setup PostgreSQL Database**
```bash
# Create database
createdb lims_qms

# Or using psql
psql -U postgres
CREATE DATABASE lims_qms;
\q
```

5. **Configure Environment Variables**
```bash
cp .env.example .env
# Edit .env file with your database credentials and other settings
```

6. **Initialize Database**
```bash
python database/init_db.py
```

7. **Run Backend Server**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

8. **Run Frontend (in new terminal)**
```bash
streamlit run frontend/app.py
```

9. **Access the Application**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## Docker Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Quick Start with Docker

1. **Clone Repository**
```bash
git clone https://github.com/ganeshgowri-asa-et/lims-qms-platform.git
cd lims-qms-platform
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env if needed
```

3. **Build and Start Services**
```bash
docker-compose up -d
```

4. **Initialize Database**
```bash
docker-compose exec backend python database/init_db.py
```

5. **Access Application**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### Docker Commands

```bash
# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Scale services
docker-compose up -d --scale backend=2
```

## Production Deployment

### Cloud Deployment Options

#### 1. AWS Deployment

**Using ECS/Fargate:**
```bash
# Build and push Docker images to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag lims-qms-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/lims-qms-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/lims-qms-backend:latest

docker tag lims-qms-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/lims-qms-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/lims-qms-frontend:latest
```

**Database:**
- Use AWS RDS PostgreSQL
- Update DATABASE_URL in environment

#### 2. Azure Deployment

**Using Azure Container Instances:**
```bash
# Login to Azure
az login

# Create resource group
az group create --name lims-qms-rg --location eastus

# Deploy container
az container create --resource-group lims-qms-rg \
  --name lims-qms-backend \
  --image <registry>/lims-qms-backend:latest \
  --cpu 2 --memory 4 \
  --environment-variables DATABASE_URL=<connection-string>
```

#### 3. Google Cloud Platform

**Using Cloud Run:**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/<project-id>/lims-qms-backend
gcloud run deploy lims-qms-backend --image gcr.io/<project-id>/lims-qms-backend --platform managed
```

### Production Best Practices

1. **Security**
   - Change default admin password immediately
   - Use strong SECRET_KEY
   - Enable HTTPS/SSL
   - Configure CORS properly
   - Use environment variables for secrets

2. **Database**
   - Use managed database service (RDS, Cloud SQL, etc.)
   - Enable automated backups
   - Setup read replicas for scalability
   - Monitor database performance

3. **Monitoring**
   - Setup application monitoring (New Relic, DataDog)
   - Configure log aggregation (ELK, Splunk)
   - Setup alerts for critical errors
   - Monitor resource usage

4. **Scaling**
   - Use load balancer
   - Enable auto-scaling
   - Setup CDN for static files
   - Cache frequently accessed data

## Database Setup

### PostgreSQL Configuration

1. **Create Database**
```sql
CREATE DATABASE lims_qms;
CREATE USER lims_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE lims_qms TO lims_user;
```

2. **Performance Tuning**
```sql
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 8MB
```

3. **Backup Strategy**
```bash
# Daily backup
pg_dump -U lims_user -d lims_qms -F c -f lims_qms_backup_$(date +%Y%m%d).dump

# Restore
pg_restore -U lims_user -d lims_qms lims_qms_backup_20240101.dump
```

## Environment Configuration

### Production Environment Variables

```bash
# Application
APP_NAME="LIMS-QMS Organization OS"
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/lims_qms
ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/lims_qms

# Security
SECRET_KEY=<generate-strong-secret-key-here>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS (adjust for your domain)
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=noreply@lims-qms.com

# AI (Optional)
ANTHROPIC_API_KEY=your_api_key_here

# Redis
REDIS_URL=redis://redis-host:6379/0
```

### Generating Secure SECRET_KEY

```python
import secrets
print(secrets.token_urlsafe(32))
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
```bash
# Check PostgreSQL is running
systemctl status postgresql

# Test connection
psql -U postgres -h localhost -d lims_qms

# Check firewall
sudo ufw status
sudo ufw allow 5432/tcp
```

2. **Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn backend.main:app --port 8001
```

3. **Permission Denied Errors**
```bash
# Fix file permissions
chmod -R 755 backend frontend
chmod -R 777 uploads

# Fix Python package permissions
pip install --user -r requirements.txt
```

4. **Docker Issues**
```bash
# Remove all containers and volumes
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs backend
```

5. **Import Errors**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python path
echo $PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/lims-qms-platform"
```

## Health Checks

### Backend Health Check
```bash
curl http://localhost:8000/health
```

### Database Health Check
```bash
psql -U postgres -d lims_qms -c "SELECT version();"
```

### Full System Check
```bash
# Check all services
docker-compose ps

# Check backend logs
docker-compose logs backend | tail -50

# Check frontend logs
docker-compose logs frontend | tail -50
```

## Performance Optimization

1. **Database Indexing**
```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_documents_level ON documents(level);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_users_username ON users(username);
```

2. **Caching**
- Enable Redis for session management
- Cache frequently accessed data
- Use CDN for static assets

3. **Application**
- Enable gzip compression
- Optimize database queries
- Use connection pooling
- Implement pagination

## Maintenance

### Regular Tasks

1. **Daily**
   - Check application logs
   - Monitor error rates
   - Verify backup completion

2. **Weekly**
   - Review system performance
   - Update dependencies
   - Clean up old logs

3. **Monthly**
   - Security audit
   - Database optimization
   - Capacity planning review

### Backup and Recovery

```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump -U lims_user lims_qms > $BACKUP_DIR/db_$TIMESTAMP.sql

# Application files backup
tar -czf $BACKUP_DIR/app_$TIMESTAMP.tar.gz /path/to/lims-qms-platform

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/db_$TIMESTAMP.sql s3://your-bucket/backups/
```

## Support

For deployment support:
- Email: support@lims-qms.com
- Documentation: https://docs.lims-qms.com
- Issues: https://github.com/ganeshgowri-asa-et/lims-qms-platform/issues
