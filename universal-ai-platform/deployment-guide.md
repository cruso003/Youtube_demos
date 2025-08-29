# NexusAI Cloud Deployment Guide
# Deploy to nexus.bits-innovate.com

## OPTION 1: DigitalOcean (Great for Africa)
# - Cape Town datacenter available
# - $5/month droplet sufficient for testing
# - Easy Docker deployment

## OPTION 2: AWS (Professional choice)
# - Cape Town region (af-south-1)
# - EC2 t3.micro (free tier eligible)
# - Professional infrastructure

## OPTION 3: Google Cloud (Good performance)
# - Johannesburg region (africa-south1)
# - Compute Engine e2-micro
# - $10/month credit

## OPTION 4: Railway (Easiest deployment)
# - Deploy directly from Docker Hub
# - Automatic domain: nexusai.up.railway.app
# - Then CNAME to nexus.bits-innovate.com

## STEP-BY-STEP DEPLOYMENT

### 1. DigitalOcean Deployment (Recommended)
```bash
# Create droplet in Cape Town
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy NexusAI
git clone https://github.com/cruso003/Youtube_demos.git
cd Youtube_demos/universal-ai-platform
cp .env.example .env
# Edit .env with your API keys
docker-compose -f docker-compose-hub.yml up -d
```

### 2. DNS Configuration
```
Type: A Record
Name: nexus
Value: [Your Droplet IP]
TTL: 300
```

### 3. SSL Setup (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d nexus.bits-innovate.com
```
