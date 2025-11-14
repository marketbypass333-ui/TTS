#!/usr/bin/env python3
"""
Docker Compose configuration for Thai TTS Development Environment
Quick Win #2: สร้าง Docker compose สำหรับ development environment
"""

import os

# Docker Compose for Thai TTS Development
docker_compose_content = """
version: '3.8'

services:
  # Main TTS Service
  thai-tts:
    build: 
      context: .
      dockerfile: Dockerfile.thai-tts
    container_name: thai-tts-dev
    ports:
      - "8000:8000"  # REST API
      - "8001:8001"  # WebSocket
      - "8080:8080"  # Web Dashboard
    volumes:
      - ./models:/app/models
      - ./data:/app/data
      - ./output:/app/output
      - ./config:/app/config
    environment:
      - PYTHONPATH=/app
      - CUDA_VISIBLE_DEVICES=0
      - TTS_MODEL_PATH=/app/models
      - THAI_DATASET_PATH=/app/data/thai
      - CACHE_DIR=/app/cache
    depends_on:
      - redis
      - postgres
    networks:
      - thai-tts-network
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Redis for Caching
  redis:
    image: redis:7-alpine
    container_name: thai-tts-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - thai-tts-network
    restart: unless-stopped
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru

  # PostgreSQL for Metadata
  postgres:
    image: postgres:15-alpine
    container_name: thai-tts-postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    environment:
      - POSTGRES_DB=thai_tts_db
      - POSTGRES_USER=thai_tts_user
      - POSTGRES_PASSWORD=thai_tts_password
    networks:
      - thai-tts-network
    restart: unless-stopped

  # Monitoring - Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: thai-tts-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - thai-tts-network
    restart: unless-stopped

  # Monitoring - Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: thai-tts-grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=thai_tts_admin
    networks:
      - thai-tts-network
    restart: unless-stopped

  # Load Balancer - Nginx
  nginx:
    image: nginx:alpine
    container_name: thai-tts-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - thai-tts
    networks:
      - thai-tts-network
    restart: unless-stopped

  # Jupyter Notebook for Development
  jupyter:
    build:
      context: .
      dockerfile: Dockerfile.jupyter
    container_name: thai-tts-jupyter
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/app/notebooks
      - ./data:/app/data
      - ./models:/app/models
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - JUPYTER_TOKEN=thai_tts_jupyter
    networks:
      - thai-tts-network
    restart: unless-stopped

volumes:
  redis-data:
  postgres-data:
  prometheus-data:
  grafana-data:

networks:
  thai-tts-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
"""

# Dockerfile for main Thai TTS service
dockerfile_content = """
FROM nvidia/cuda:11.8-devel-ubuntu20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3-pip \
    git \
    wget \
    curl \
    ffmpeg \
    libsndfile1 \
    portaudio19-dev \
    espeak-ng \
    espeak-data \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.thai.txt .
RUN pip3 install --no-cache-dir -r requirements.thai.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/models /app/data /app/output /app/cache /app/config

# Download Thai language models and data
RUN python3 scripts/download_thai_models.py

# Expose ports
EXPOSE 8000 8001 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python3", "app.py"]
"""

# Requirements file for Thai TTS
requirements_content = """
# Core TTS dependencies
TTS>=0.22.0
torch>=2.0.0
torchaudio>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
librosa>=0.10.0
soundfile>=0.12.0

# Thai language processing
pythainlp>=4.0.0
pyicu>=2.10.0
marisa-trie>=0.7.5

# Web framework
fastapi>=0.100.0
uvicorn[standard]>=0.22.0
websockets>=11.0.0
python-multipart>=0.0.6

# Database and caching
redis>=4.5.0
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0
alembic>=1.10.0

# Monitoring and logging
prometheus-client>=0.16.0
python-json-logger>=2.0.0
structlog>=23.0.0

# Utilities
pydantic>=2.0.0
python-dotenv>=1.0.0
click>=8.1.0
rich>=13.0.0
typer>=0.9.0

# Development tools
jupyter>=1.0.0
jupyterlab>=4.0.0
ipywidgets>=8.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.15.0

# Audio processing
pydub>=0.25.0
resampy>=0.4.0
webrtcvad>=2.0.10

# Thai specific
swathai>=1.0.0
thai-segmenter>=0.1.0
"""

# Create docker-compose.yml
with open('/home/user/webapp/docker-compose.thai.yml', 'w', encoding='utf-8') as f:
    f.write(docker_compose_content)

# Create Dockerfile
with open('/home/user/webapp/Dockerfile.thai-tts', 'w', encoding='utf-8') as f:
    f.write(dockerfile_content)

# Create requirements file
with open('/home/user/webapp/requirements.thai.txt', 'w', encoding='utf-8') as f:
    f.write(requirements_content)

# Create startup script
startup_script = """#!/bin/bash
# Thai TTS Development Environment Startup Script

echo "🚀 Starting Thai TTS Development Environment..."

# Create necessary directories
mkdir -p models data output cache config notebooks monitoring/grafana/provisioning nginx/ssl sql

# Set permissions
chmod 755 models data output cache config

# Create .env file if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Thai TTS Environment Variables
PYTHONPATH=/app
CUDA_VISIBLE_DEVICES=0
TTS_MODEL_PATH=/app/models
THAI_DATASET_PATH=/app/data/thai
CACHE_DIR=/app/cache
REDIS_URL=redis://redis:6379
DATABASE_URL=postgresql://thai_tts_user:thai_tts_password@postgres:5432/thai_tts_db
EOF
fi

# Create nginx configuration
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream thai-tts {
        server thai-tts:8000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            proxy_pass http://thai-tts;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location /ws {
            proxy_pass http://thai-tts:8001;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF

# Create prometheus configuration
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'thai-tts'
    static_configs:
      - targets: ['thai-tts:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
EOF

# Create SQL initialization
cat > sql/init.sql << 'EOF'
-- Thai TTS Database Schema
CREATE TABLE IF NOT EXISTS audio_requests (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    audio_path VARCHAR(500),
    duration FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

CREATE TABLE IF NOT EXISTS voice_clones (
    id SERIAL PRIMARY KEY,
    voice_name VARCHAR(100) NOT NULL,
    model_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS api_usage (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(100),
    method VARCHAR(10),
    status_code INTEGER,
    response_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF

echo "✅ Configuration files created successfully!"
echo ""
echo "🐳 Starting Docker Compose..."
echo ""

# Start the services
docker-compose -f docker-compose.thai.yml up -d

echo ""
echo "🎉 Thai TTS Development Environment is starting up!"
echo ""
echo "Services will be available at:"
echo "  - TTS API:      http://localhost:8000"
echo "  - WebSocket:    ws://localhost:8001"
echo "  - Web Dashboard: http://localhost:8080"
echo "  - Grafana:      http://localhost:3000 (admin/thai_tts_admin)"
echo "  - Prometheus:   http://localhost:9090"
echo "  - Jupyter:      http://localhost:8888 (token: thai_tts_jupyter)"
echo ""
echo "To stop the environment:"
echo "  docker-compose -f docker-compose.thai.yml down"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.thai.yml logs -f"
"""

with open('/home/user/webapp/start_thai_tts_dev.sh', 'w', encoding='utf-8') as f:
    f.write(startup_script)

# Make the script executable
os.chmod('/home/user/webapp/start_thai_tts_dev.sh', 0o755)

print("✅ Docker Compose configuration created successfully!")
print("\nTo start the Thai TTS development environment:")
print("1. Run: ./start_thai_tts_dev.sh")
print("2. Access services at the URLs provided")
print("\nThis implements Quick Win #2: สร้าง Docker compose สำหรับ development environment")