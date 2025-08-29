#!/bin/bash

echo "🧹 Cleaning up NexusAI project..."

# Remove Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true

# Remove virtual environment (we use Docker now)
echo "Removing virtual environment..."
rm -rf venv/

# Remove old deployment scripts (keep only the working ones)
echo "Removing old deployment scripts..."
rm -f deploy-railway.sh
rm -f deploy-server.sh 
rm -f deploy.sh
rm -f quick-deploy-public.sh
rm -f railway-deploy.txt
rm -f requirements-railway.txt
rm -f requirements-vercel.txt
rm -f railway.json
rm -f vercel.json

# Remove log files and temp files
echo "Removing log files..."
rm -rf logs/
rm -f usage_tracking.db
rm -f *.log

# Remove unnecessary docs (keep main docs)
echo "Cleaning up documentation..."
rm -f prompt.md

# Clean up any DS_Store files (macOS)
echo "Removing macOS system files..."
find . -name ".DS_Store" -delete 2>/dev/null || true

# Remove any backup files
echo "Removing backup files..."
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*~" -delete 2>/dev/null || true

# Clean up examples (they're not needed for production)
echo "Removing example files..."
rm -rf examples/

# Clean up any test database files
echo "Removing test files..."
rm -f *.db

echo "✅ Cleanup complete!"
echo ""
echo "📁 Remaining important files:"
echo "   - Core application code (api_gateway/, adapters/, services/)"
echo "   - Docker configuration (Dockerfile, docker-compose-hub.yml)"
echo "   - Production deployment (deploy-digitalocean.sh, deploy-nexusai.sh)"
echo "   - Client SDKs (client_sdks/)"
echo "   - Documentation (docs/, website/)"
echo "   - Configuration (.env files, requirements.txt)"
