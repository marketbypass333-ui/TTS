#!/bin/bash
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
