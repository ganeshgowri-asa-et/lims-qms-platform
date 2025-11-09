# Docker Setup Guide

## Quick Start with Docker Compose

### Prerequisites
- Docker Desktop or Docker Engine
- Docker Compose

### Step 1: Start All Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- FastAPI server on port 8000
- Streamlit UI on port 8501

### Step 2: Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501

### Step 3: View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f ui
docker-compose logs -f db
```

### Step 4: Stop Services

```bash
docker-compose down
```

### Step 5: Reset Everything (including data)

```bash
docker-compose down -v
```

## Individual Container Commands

### Build Images

```bash
docker-compose build
```

### Rebuild Without Cache

```bash
docker-compose build --no-cache
```

### Run Specific Service

```bash
docker-compose up api
```

## Database Management

### Access PostgreSQL

```bash
docker-compose exec db psql -U postgres -d lims_qms
```

### Backup Database

```bash
docker-compose exec db pg_dump -U postgres lims_qms > backup.sql
```

### Restore Database

```bash
docker-compose exec -T db psql -U postgres lims_qms < backup.sql
```

## Development Mode

For development with hot-reload:

```bash
docker-compose up
```

The API and UI will automatically reload when you change the code.

## Production Deployment

For production, modify `docker-compose.yml`:

1. Remove `--reload` flag from API command
2. Set proper environment variables
3. Use production-grade database password
4. Configure SSL/TLS
5. Use volume mounts for persistent data

## Troubleshooting

### Database Connection Issues

```bash
# Check if database is running
docker-compose ps

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### API Not Starting

```bash
# Check API logs
docker-compose logs api

# Rebuild API container
docker-compose up -d --build api
```

### Port Already in Use

```bash
# Change ports in docker-compose.yml
# For example, change 8000:8000 to 8001:8000
```

## Environment Variables

Create a `.env` file for custom configuration:

```env
POSTGRES_DB=lims_qms
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password
DATABASE_URL=postgresql://postgres:secure_password@db:5432/lims_qms
```

## Health Checks

Check service health:

```bash
# API health
curl http://localhost:8000/health

# Database health
docker-compose exec db pg_isready -U postgres
```
