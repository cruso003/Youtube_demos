#!/bin/bash

# NexusAI DigitalOcean Deployment Script
# Deploy NexusAI with full power on DigitalOcean

set -e

echo "🌊 NexusAI DigitalOcean Full Power Deployment"
echo "============================================="

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    print_warning "DigitalOcean CLI (doctl) not found."
    print_info "Please install it:"
    echo "  macOS: brew install doctl"
    echo "  Linux: snap install doctl"
    echo "  Or download from: https://github.com/digitalocean/doctl/releases"
    echo ""
    read -p "Press Enter after installing doctl..."
fi

# Auth check
print_info "Checking DigitalOcean authentication..."
if ! doctl account get > /dev/null 2>&1; then
    print_warning "Please authenticate with DigitalOcean:"
    print_info "1. Get your API token from: https://cloud.digitalocean.com/account/api/tokens"
    print_info "2. Run: doctl auth init"
    echo ""
    read -p "Press Enter after authenticating..."
fi

print_status "DigitalOcean CLI authenticated"

# Droplet configuration
DROPLET_NAME="nexusai-production"
DROPLET_SIZE="s-2vcpu-4gb"  # $24/month - perfect for NexusAI
DROPLET_IMAGE="ubuntu-22-04-x64"
DROPLET_REGION="fra1"  # Frankfurt - closest to Africa

print_info "Creating DigitalOcean Droplet for NexusAI..."
echo "  Name: $DROPLET_NAME"
echo "  Size: $DROPLET_SIZE (2 vCPUs, 4GB RAM)"
echo "  Region: $DROPLET_REGION (Frankfurt - closest to Africa)"
echo "  Image: $DROPLET_IMAGE"
echo ""

# Create SSH key if it doesn't exist
SSH_KEY_NAME="nexusai-key"
if ! doctl compute ssh-key list | grep -q "$SSH_KEY_NAME"; then
    print_info "Creating SSH key for secure access..."
    
    if [[ ! -f ~/.ssh/id_rsa ]]; then
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    fi
    
    doctl compute ssh-key import "$SSH_KEY_NAME" --public-key-file ~/.ssh/id_rsa.pub
    print_status "SSH key created and uploaded"
fi

# Create droplet
print_info "Creating droplet... (this takes ~1 minute)"
DROPLET_ID=$(doctl compute droplet create $DROPLET_NAME \
    --size $DROPLET_SIZE \
    --image $DROPLET_IMAGE \
    --region $DROPLET_REGION \
    --ssh-keys $(doctl compute ssh-key list --format ID --no-header | head -1) \
    --wait \
    --format ID \
    --no-header)

print_status "Droplet created! ID: $DROPLET_ID"

# Get IP address
DROPLET_IP=$(doctl compute droplet get $DROPLET_ID --format PublicIPv4 --no-header)
print_status "Droplet IP: $DROPLET_IP"

# Wait for SSH to be ready
print_info "Waiting for SSH to be ready..."
while ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@$DROPLET_IP "echo 'SSH Ready'" > /dev/null 2>&1; do
    echo -n "."
    sleep 5
done
echo ""
print_status "SSH connection ready"

# Create deployment script for the server
cat > deploy-server.sh << 'EOF'
#!/bin/bash

# NexusAI Server Setup Script
set -e

echo "🚀 Setting up NexusAI on DigitalOcean Droplet"

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install nginx for SSL termination
apt install -y nginx certbot python3-certbot-nginx

# Create app directory
mkdir -p /opt/nexusai
cd /opt/nexusai

# Create docker-compose for production
cat > docker-compose.yml << 'COMPOSE_EOF'
version: '3.8'

services:
  nexusai-platform:
    image: bitsinfo/nexusai:latest
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
      - PORT=8000
      - HOST=0.0.0.0
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

volumes:
  redis_data:
COMPOSE_EOF

# Create logs directory
mkdir -p logs

# Start services
docker-compose up -d

echo "✅ NexusAI is running on port 8000"
echo "🌐 Access via: http://$(curl -s ifconfig.me):8000/health"
EOF

# Copy and run the deployment script
print_info "Deploying NexusAI to the droplet..."
scp -o StrictHostKeyChecking=no deploy-server.sh root@$DROPLET_IP:/tmp/
ssh -o StrictHostKeyChecking=no root@$DROPLET_IP "chmod +x /tmp/deploy-server.sh && /tmp/deploy-server.sh"

# Clean up
rm deploy-server.sh

print_status "🎉 NexusAI deployed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "  🌐 Server IP: $DROPLET_IP"
echo "  🔗 Health Check: http://$DROPLET_IP:8000/health"
echo "  🎯 API Gateway: http://$DROPLET_IP:8000/api/v1/"
echo ""
echo "🔧 Next Steps:"
echo "  1. Set up DNS: nexus.bits-innovate.com → $DROPLET_IP"
echo "  2. Configure SSL: ssh root@$DROPLET_IP 'certbot --nginx -d nexus.bits-innovate.com'"
echo "  3. Add environment variables for full features"
echo ""
echo "💰 Monthly Cost: ~$24 (8+ months with your $200 credits!)"
echo ""
print_info "SSH Access: ssh root@$DROPLET_IP"
