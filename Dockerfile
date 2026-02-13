# Multi-stage Dockerfile for AayurAI Full-Stack Application
# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm ci --only=production

# Copy frontend source
COPY frontend/ ./

# Build frontend for production
RUN npm run build

# Stage 2: Setup Backend with Frontend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend application
COPY backend/ ./backend/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create necessary directories
RUN mkdir -p /app/backend/logs \
    && mkdir -p /app/backend/uploads \
    && mkdir -p /app/models

# Copy models if they exist (optional)
COPY models ./models 2>/dev/null || echo "No models directory found, skipping..."

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Change to backend directory
WORKDIR /app/backend

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
