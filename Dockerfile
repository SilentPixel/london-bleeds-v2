# Dockerfile for London Bleeds FastAPI backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY backend/ ./backend/

# Create database directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Set environment variables
ENV DATABASE_URL=sqlite:///data/game.db
ENV PYTHONPATH=/app/backend

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


