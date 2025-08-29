# Deployment Guide

This guide covers deploying the Universal AI Agent Platform in production environments, from single-server setups to enterprise-scale deployments.

## Quick Deployment Options

### 1. Docker Deployment (Recommended)

The easiest way to deploy the platform is using Docker containers.

#### Single Container Setup

```bash
# Download the NexusAI platform
wget https://github.com/bits-innovate/nexusai-platform/releases/latest/download/nexusai-platform.tar.gz
tar -xzf nexusai-platform.tar.gz
cd nexusai-platform

# Build the Docker image
docker build -t nexusai-platform .

# Run with environment variables
docker run -d \
  --name nexusai \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e DEEPGRAM_API_KEY=your_key \
  nexusai-platform
```

#### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  universal-ai-platform:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEEPGRAM_API_KEY=${DEEPGRAM_API_KEY}
      - CARTESIA_API_KEY=${CARTESIA_API_KEY}
      - LIVEKIT_URL=${LIVEKIT_URL}
      - LIVEKIT_API_KEY=${LIVEKIT_API_KEY}
      - LIVEKIT_API_SECRET=${LIVEKIT_API_SECRET}
      - DATABASE_URL=postgresql://user:pass@db:5432/universal_ai
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=universal_ai
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - universal-ai-platform
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

```bash
# Deploy with Docker Compose
docker-compose up -d
```

### 2. Kubernetes Deployment

For enterprise-scale deployments, use Kubernetes.

#### Namespace and ConfigMap

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: universal-ai
---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: universal-ai-config
  namespace: universal-ai
data:
  DATABASE_URL: "postgresql://user:pass@postgres:5432/universal_ai"
  REDIS_URL: "redis://redis:6379"
  LOG_LEVEL: "INFO"
```

#### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: universal-ai-secrets
  namespace: universal-ai
type: Opaque
stringData:
  OPENAI_API_KEY: "your_openai_key"
  DEEPGRAM_API_KEY: "your_deepgram_key"
  CARTESIA_API_KEY: "your_cartesia_key"
  LIVEKIT_API_KEY: "your_livekit_key"
  LIVEKIT_API_SECRET: "your_livekit_secret"
```

#### Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: universal-ai-platform
  namespace: universal-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: universal-ai-platform
  template:
    metadata:
      labels:
        app: universal-ai-platform
    spec:
      containers:
      - name: universal-ai
        image: universal-ai-platform:latest
        ports:
        - containerPort: 8000
        env:
        - name: PORT
          value: "8000"
        envFrom:
        - configMapRef:
            name: universal-ai-config
        - secretRef:
            name: universal-ai-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 15
---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: universal-ai-service
  namespace: universal-ai
spec:
  selector:
    app: universal-ai-platform
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: universal-ai-ingress
  namespace: universal-ai
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: universal-ai-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: universal-ai-service
            port:
              number: 8000
```

#### Deploy to Kubernetes

```bash
# Apply all configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n universal-ai
kubectl get services -n universal-ai
kubectl get ingress -n universal-ai
```

### 3. Cloud Provider Deployments

#### AWS ECS with Fargate

```json
{
  "family": "universal-ai-platform",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "universal-ai",
      "image": "your-account.dkr.ecr.region.amazonaws.com/universal-ai-platform:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "PORT",
          "value": "8000"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:universal-ai/openai-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/universal-ai-platform",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

#### Google Cloud Run

```yaml
# cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: universal-ai-platform
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 100
      containers:
      - image: gcr.io/your-project/universal-ai-platform:latest
        ports:
        - containerPort: 8000
        env:
        - name: PORT
          value: "8000"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: universal-ai-secrets
              key: openai-api-key
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
          requests:
            cpu: "1"
            memory: "1Gi"
```

```bash
# Deploy to Cloud Run
gcloud run services replace cloudrun.yaml --region=us-central1
```

#### Azure Container Instances

```yaml
# azure-container.yaml
apiVersion: '2019-12-01'
location: eastus
properties:
  containers:
  - name: universal-ai-platform
    properties:
      image: youracr.azurecr.io/universal-ai-platform:latest
      ports:
      - port: 8000
        protocol: TCP
      environmentVariables:
      - name: PORT
        value: "8000"
      - name: OPENAI_API_KEY
        secureValue: "your_openai_key"
      resources:
        requests:
          cpu: 1
          memoryInGB: 2
  osType: Linux
  ipAddress:
    type: Public
    ports:
    - port: 8000
      protocol: TCP
  restartPolicy: Always
tags:
  environment: production
  service: universal-ai-platform
```

## Production Configuration

### Environment Variables

Create a comprehensive `.env` file for production:

```bash
# Production .env file

# Service Configuration
NODE_ENV=production
PORT=8000
HOST=0.0.0.0

# AI Service API Keys
OPENAI_API_KEY=your_openai_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
CARTESIA_API_KEY=your_cartesia_api_key

# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/universal_ai
DATABASE_POOL_SIZE=20
DATABASE_MAX_CONNECTIONS=100

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# Security
JWT_SECRET=your_jwt_secret_key
API_KEY_ENCRYPTION_KEY=your_encryption_key
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Rate Limiting
RATE_LIMIT_WINDOW_MS=3600000  # 1 hour
RATE_LIMIT_MAX_REQUESTS=1000

# Monitoring
LOG_LEVEL=info
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30000

# Feature Flags
VOICE_ENABLED=true
VISION_ENABLED=true
CUSTOM_ADAPTERS_ENABLED=true

# Billing
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# External Services
SENDGRID_API_KEY=your_sendgrid_key
SLACK_WEBHOOK_URL=your_slack_webhook
```

### Nginx Configuration

```nginx
# nginx/nginx.conf
upstream universal_ai_backend {
    server universal-ai-platform:8000;
    # Add more servers for load balancing
    # server universal-ai-platform-2:8000;
    # server universal-ai-platform-3:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Proxy Configuration
    location / {
        proxy_pass http://universal_ai_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 8k;
        proxy_buffers 32 8k;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://universal_ai_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://universal_ai_backend/health;
    }

    # Static files (if any)
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Database Setup

### PostgreSQL Configuration

```sql
-- Create database and user
CREATE DATABASE universal_ai;
CREATE USER universal_ai_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE universal_ai TO universal_ai_user;

-- Connect to the database
\c universal_ai;

-- Create tables
CREATE TABLE IF NOT EXISTS usage_metrics (
    id SERIAL PRIMARY KEY,
    client_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    metric_type VARCHAR(50) NOT NULL,
    metric_value INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS billing_plans (
    id SERIAL PRIMARY KEY,
    plan_name VARCHAR(100) NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    price_per_message DECIMAL(8,4) DEFAULT 0,
    price_per_image DECIMAL(8,4) DEFAULT 0,
    price_per_voice_minute DECIMAL(8,4) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    client_id VARCHAR(255),
    agent_config JSONB,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_usage_metrics_client_id ON usage_metrics(client_id);
CREATE INDEX idx_usage_metrics_timestamp ON usage_metrics(timestamp);
CREATE INDEX idx_sessions_session_id ON sessions(session_id);
CREATE INDEX idx_sessions_client_id ON sessions(client_id);

-- Insert default billing plans
INSERT INTO billing_plans (plan_name, base_price, price_per_message, price_per_image, price_per_voice_minute) VALUES
('starter', 49.00, 0.01, 0.05, 0.10),
('professional', 199.00, 0.008, 0.04, 0.08),
('enterprise', 999.00, 0.005, 0.03, 0.06);
```

### Redis Configuration

```bash
# redis/redis.conf
# Basic configuration
bind 127.0.0.1
port 6379
timeout 300
keepalive 60

# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Security
requirepass your_redis_password

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log

# Performance
tcp-backlog 511
tcp-keepalive 300
```

## Monitoring and Observability

### Prometheus Metrics

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Define metrics
REQUEST_COUNT = Counter('universal_ai_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('universal_ai_request_duration_seconds', 'Request duration')
ACTIVE_SESSIONS = Gauge('universal_ai_active_sessions', 'Number of active sessions')
AI_API_CALLS = Counter('universal_ai_api_calls_total', 'AI API calls', ['service', 'status'])

def setup_metrics_endpoint(app):
    """Add metrics endpoint to Flask app"""
    @app.route('/metrics')
    def metrics():
        return generate_latest()
```

### Health Checks

```python
# health/checks.py
import time
import redis
import psycopg2
from flask import jsonify

class HealthChecker:
    def __init__(self, redis_url, db_url):
        self.redis_url = redis_url
        self.db_url = db_url
    
    def check_redis(self):
        """Check Redis connectivity"""
        try:
            r = redis.from_url(self.redis_url)
            r.ping()
            return {'status': 'healthy', 'response_time': 0}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    def check_database(self):
        """Check PostgreSQL connectivity"""
        try:
            start_time = time.time()
            conn = psycopg2.connect(self.db_url)
            conn.close()
            response_time = time.time() - start_time
            return {'status': 'healthy', 'response_time': response_time}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    def check_ai_services(self):
        """Check AI service connectivity"""
        # Implement checks for OpenAI, Deepgram, etc.
        return {'status': 'healthy'}
    
    def get_health_status(self):
        """Get overall health status"""
        checks = {
            'redis': self.check_redis(),
            'database': self.check_database(),
            'ai_services': self.check_ai_services()
        }
        
        overall_status = 'healthy' if all(
            check['status'] == 'healthy' for check in checks.values()
        ) else 'unhealthy'
        
        return {
            'status': overall_status,
            'timestamp': time.time(),
            'checks': checks
        }

# Add to your Flask app
@app.route('/health')
def health_check():
    health_checker = HealthChecker(redis_url, db_url)
    return jsonify(health_checker.get_health_status())
```

### Logging Configuration

```python
# logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured logging"""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler for production
    if os.environ.get('NODE_ENV') == 'production':
        file_handler = logging.FileHandler('/var/log/universal-ai/app.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
```

## Security Best Practices

### 1. API Security

```python
# security/auth.py
import jwt
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('Authorization')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        if not api_key.startswith('Bearer '):
            return jsonify({'error': 'Invalid API key format'}), 401
        
        key = api_key.split('Bearer ')[1]
        if not validate_api_key(key):
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def validate_api_key(key):
    """Validate API key against database"""
    # Implement your key validation logic
    return True
```

### 2. Input Validation

```python
# security/validation.py
from marshmallow import Schema, fields, ValidationError

class AgentCreateSchema(Schema):
    instructions = fields.Str(required=True, validate=lambda x: len(x) <= 1000)
    capabilities = fields.List(
        fields.Str(validate=lambda x: x in ['text', 'voice', 'vision']),
        required=True
    )
    business_logic_adapter = fields.Str(validate=lambda x: x in ALLOWED_ADAPTERS)
    custom_settings = fields.Dict()

def validate_request(schema_class):
    """Decorator for request validation"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            schema = schema_class()
            try:
                data = schema.load(request.json)
                request.validated_data = data
                return f(*args, **kwargs)
            except ValidationError as err:
                return jsonify({'error': 'Validation error', 'details': err.messages}), 400
        return decorated_function
    return decorator
```

### 3. Rate Limiting

```python
# security/rate_limiting.py
import redis
import time
from flask import request, jsonify

class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def is_allowed(self, key, limit, window):
        """Check if request is within rate limit"""
        current_time = time.time()
        pipeline = self.redis.pipeline()
        
        # Remove expired entries
        pipeline.zremrangebyscore(key, 0, current_time - window)
        
        # Count current requests
        pipeline.zcard(key)
        
        # Add current request
        pipeline.zadd(key, {str(current_time): current_time})
        
        # Set expiration
        pipeline.expire(key, int(window))
        
        results = pipeline.execute()
        request_count = results[1]
        
        return request_count < limit

def rate_limit(limit=100, window=3600):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            api_key = request.headers.get('Authorization', '').split('Bearer ')[-1]
            
            key = f"rate_limit:{api_key or client_ip}"
            
            if not rate_limiter.is_allowed(key, limit, window):
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

## Scaling Strategies

### Horizontal Scaling

1. **Load Balancing**: Use nginx, HAProxy, or cloud load balancers
2. **Session Affinity**: Implement sticky sessions or session storage
3. **Database Scaling**: Read replicas, connection pooling
4. **Caching**: Redis cluster for distributed caching

### Performance Optimization

1. **Connection Pooling**: Optimize database connections
2. **Async Processing**: Use Celery for background tasks
3. **CDN**: Use CloudFlare or AWS CloudFront for static assets
4. **Compression**: Enable gzip/brotli compression

### Monitoring at Scale

1. **Distributed Tracing**: Use Jaeger or Zipkin
2. **Centralized Logging**: ELK stack or Fluentd
3. **Metrics Collection**: Prometheus + Grafana
4. **Alerting**: PagerDuty, OpsGenie integration

---

**Next**: Learn about [Business Logic Adapters](/docs/guides/adapters) or check out the [API Reference](/docs/api) for detailed endpoint documentation.