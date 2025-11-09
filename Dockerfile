FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p backend/api/routes backend/database backend/services frontend/utils

# Expose ports
EXPOSE 8000 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["sh", "-c", "python main.py & cd frontend && streamlit run app.py --server.address=0.0.0.0"]
