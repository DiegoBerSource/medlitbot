# MedLitBot Infrastructure on Hetzner Cloud

This directory contains the Pulumi infrastructure-as-code configuration for deploying MedLitBot on Hetzner Cloud with minimal resources for cost optimization.

## 🏗️ Infrastructure Overview

### Components
- **Hetzner Cloud Server**: CAX11 ARM64 (1 vCPU, 4GB RAM, 40GB SSD) - €3.90/month
- **Block Storage**: 20GB volume for persistent data - €10/month  
- **Networking**: Private network with firewall rules
- **Services**: Django app, PostgreSQL, Redis, Celery, Nginx (all containerized)

### Total Estimated Cost: ~€14/month

## 📋 Prerequisites

1. **Hetzner Cloud Account**: Sign up at https://www.hetzner.com/cloud
2. **Hetzner Cloud API Token**: Create in Hetzner Cloud Console → Security → API tokens
3. **SSH Key Pair**: Generate with `ssh-keygen -t rsa -b 4096 -C "medlitbot-deploy"`
4. **Pulumi CLI**: Install from https://www.pulumi.com/docs/install/
5. **Python 3.8+**: For running deployment scripts

## 🏗️ ARM64 Architecture

This infrastructure now uses **ARM64 servers (CAX series)** by default, which offer:
- **Better Performance/Price**: ~20% cheaper than equivalent x86 servers
- **Energy Efficiency**: Lower power consumption 
- **Modern Architecture**: Latest ARM Neoverse cores
- **Full Compatibility**: Ubuntu 22.04 and Docker containers work seamlessly on ARM64

**Note**: Most Python packages and Docker images support ARM64. If you encounter compatibility issues with specific packages, you can switch to x86 servers by setting `server_type` to `cx11` or `cx21`.

## 🚀 Quick Deployment

### 1. Setup Environment

```bash
# Navigate to infrastructure directory
cd infrastructure

# Install dependencies
pip install -r requirements.txt

# Initialize Pulumi
pulumi login  # Follow prompts to create account or login

# Create new stack
pulumi stack init prod
```

### 2. Configure Secrets

```bash
# Hetzner Cloud API token
pulumi config set hcloud:token YOUR_HETZNER_API_TOKEN --secret

# SSH public key for server access
pulumi config set ssh_public_key "$(cat ~/.ssh/id_rsa.pub)"

# Django secret key
pulumi config set django_secret_key "$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" --secret

# Optional: Custom domain
pulumi config set domain_name "your-domain.com"

# Optional: Allowed hosts for Django
pulumi config set allowed_hosts "your-domain.com,www.your-domain.com"
```

### 3. Deploy Infrastructure

```bash
# Preview deployment
pulumi preview

# Deploy infrastructure
pulumi up

# Get server IP
pulumi stack output server_public_ip
```

### 4. Deploy Application

```bash
# Option 1: Use automated deployment script
python deploy.py

# Option 2: Manual deployment
export SERVER_IP=$(pulumi stack output server_public_ip)
ssh root@$SERVER_IP

# On server:
cd /mnt/medlitbot-data/app
docker-compose -f docker-compose.prod.yml up -d
```

## ⚙️ Configuration Options

### Server Configuration

```bash
# Use different server type (default: cax11 ARM64)
pulumi config set server_type cax21  # 2 vCPU ARM64, 8GB RAM - €7.90/month
pulumi config set server_type cx11   # 1 vCPU x86, 4GB RAM - €4.90/month

# Change location (default: nbg1 - Nuremberg)  
pulumi config set server_location fsn1  # Falkenstein
pulumi config set server_location hel1  # Helsinki
```

### Storage Configuration

```bash
# Increase storage size (default: 20GB)
pulumi config set volume_size 50  # 50GB - €25/month
```

## 📊 Resource Specifications

### CAX11 Server (Minimal - ARM64)
- **vCPU**: 1 dedicated ARM64 vCPU
- **RAM**: 4GB
- **SSD**: 40GB local storage  
- **Network**: 20TB traffic included
- **Cost**: €3.90/month

### CAX21 Server (Recommended - ARM64)
- **vCPU**: 2 dedicated ARM64 vCPUs
- **RAM**: 8GB
- **SSD**: 80GB local storage
- **Network**: 20TB traffic included  
- **Cost**: €7.90/month

### CX11 Server (x86 Alternative)
- **vCPU**: 1 dedicated x86 vCPU
- **RAM**: 4GB
- **SSD**: 40GB local storage  
- **Network**: 20TB traffic included
- **Cost**: €4.90/month

### Block Storage
- **Performance**: Up to 3,000 IOPS
- **Backup**: Snapshots available
- **Cost**: €0.50/GB/month

## 🔧 Management Commands

### Infrastructure Management

```bash
# View stack info
pulumi stack

# View outputs
pulumi stack output

# Update infrastructure
pulumi up

# Destroy everything
pulumi destroy
```

### Application Management

```bash
export SERVER_IP=$(pulumi stack output server_public_ip)

# SSH to server
ssh root@$SERVER_IP

# View application logs
ssh root@$SERVER_IP "cd /mnt/medlitbot-data/app && docker-compose -f docker-compose.prod.yml logs"

# Restart services
ssh root@$SERVER_IP "cd /mnt/medlitbot-data/app && docker-compose -f docker-compose.prod.yml restart"

# Update application code
rsync -avz --exclude='.git' --exclude='node_modules' ../ root@$SERVER_IP:/mnt/medlitbot-data/app/
ssh root@$SERVER_IP "cd /mnt/medlitbot-data/app && docker-compose -f docker-compose.prod.yml up -d --build"
```

## 🔒 Security Setup

### SSL Certificate (Let's Encrypt)

```bash
# If using custom domain
export DOMAIN="your-domain.com"
export SERVER_IP=$(pulumi stack output server_public_ip)

# Point domain A record to server IP first, then:
ssh root@$SERVER_IP "certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN"
```

### Firewall Rules

The infrastructure automatically configures:
- SSH (port 22) - restricted to your IP
- HTTP (port 80) - open to all
- HTTPS (port 443) - open to all
- All other ports blocked

### Admin Access

Default admin user is created with:
- **Username**: admin
- **Password**: adminpass123 (⚠️ Change immediately!)

Access admin panel at: `http://your-server-ip/admin/`

## 📈 Monitoring & Maintenance

### Health Checks

```bash
# Check service status
ssh root@$SERVER_IP "cd /mnt/medlitbot-data/app && docker-compose -f docker-compose.prod.yml ps"

# Check application health
curl http://your-server-ip/health/
```

### Backups

```bash
# Database backup
ssh root@$SERVER_IP "docker exec medlitbot_postgres pg_dump -U medlitbot medlitbot > /mnt/medlitbot-data/backup-$(date +%Y%m%d).sql"

# Create volume snapshot (from Hetzner console or CLI)
pulumi stack output volume_id  # Use this ID in Hetzner console
```

### Updates

```bash
# Update application
git pull
python deploy.py  # Will redeploy with latest code

# Update system packages
ssh root@$SERVER_IP "apt update && apt upgrade -y"

# Update Docker images
ssh root@$SERVER_IP "cd /mnt/medlitbot-data/app && docker-compose -f docker-compose.prod.yml pull && docker-compose -f docker-compose.prod.yml up -d"
```

## 🐛 Troubleshooting

### Common Issues

1. **SSH Connection Refused**
   ```bash
   # Wait for server initialization (can take 2-3 minutes)
   ssh -o ConnectTimeout=10 root@$SERVER_IP 'echo ready'
   ```

2. **Application Not Loading**
   ```bash
   # Check service logs
   ssh root@$SERVER_IP "cd /mnt/medlitbot-data/app && docker-compose -f docker-compose.prod.yml logs web"
   ```

3. **Database Connection Issues**
   ```bash
   # Check database logs
   ssh root@$SERVER_IP "cd /mnt/medlitbot-data/app && docker-compose -f docker-compose.prod.yml logs postgres"
   
   # Restart database
   ssh root@$SERVER_IP "cd /mnt/medlitbot-data/app && docker-compose -f docker-compose.prod.yml restart postgres"
   ```

4. **Out of Disk Space**
   ```bash
   # Check disk usage
   ssh root@$SERVER_IP "df -h"
   
   # Clean Docker system
   ssh root@$SERVER_IP "docker system prune -f"
   
   # Increase volume size
   pulumi config set volume_size 50
   pulumi up
   ```

### Log Locations

```bash
# Application logs
/mnt/medlitbot-data/logs/django.log
/mnt/medlitbot-data/logs/celery.log

# Docker logs
docker-compose -f docker-compose.prod.yml logs [service_name]

# System logs
/var/log/cloud-init.log  # Server initialization
/var/log/nginx/access.log  # Web server access
/var/log/nginx/error.log   # Web server errors
```

## 💰 Cost Optimization

### Current Configuration (~€14/month)
- CAX11 ARM64 Server: €3.90/month
- 20GB Volume: €10/month  
- Network: Free

### Budget Options
- **Ultra-minimal**: CAX11 + 10GB volume = ~€9/month
  ```bash
  pulumi config set volume_size 10
  ```

### Scaling Up
- **Performance ARM64**: CAX21 + 50GB volume = ~€33/month
  ```bash
  pulumi config set server_type cax21
  pulumi config set volume_size 50
  ```
- **Performance x86**: CX21 + 50GB volume = ~€34/month
  ```bash
  pulumi config set server_type cx21
  pulumi config set volume_size 50
  ```

## 🚀 Next Steps

1. **Custom Domain**: Point your domain to the server IP
2. **SSL Certificate**: Run certbot for HTTPS
3. **Monitoring**: Set up monitoring with services like UptimeRobot
4. **Backup Strategy**: Implement regular database and volume backups
5. **CI/CD**: Set up automated deployments with GitHub Actions

## 📞 Support

- **Pulumi Issues**: Check outputs with `pulumi stack output`
- **Hetzner Issues**: Check Hetzner Cloud Console
- **Application Issues**: Check Docker logs and Django logs
- **SSH Issues**: Verify SSH key configuration and firewall rules
