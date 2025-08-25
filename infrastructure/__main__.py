"""
MedLitBot Infrastructure on Hetzner Cloud
Minimal resource deployment for cost optimization
"""

import pulumi
import pulumi_hcloud as hcloud
from pulumi import Config, Output
import base64

# Configuration
config = Config()
server_type = config.get("server_type") or "cax11"
server_location = config.get("server_location") or "nbg1" 
volume_size = config.get_int("volume_size") or 20
environment = config.get("environment") or "prod"
django_secret_key = config.require_secret("django_secret_key")
allowed_hosts = config.get("allowed_hosts") or "*"

# SSH Key for server access
ssh_key = hcloud.SshKey("medlitbot-ssh-key",
    name=f"medlitbot-{environment}-ssh-key",
    public_key=pulumi.Config().require("ssh_public_key")  # Set via: pulumi config set ssh_public_key "ssh-rsa AAAA..."
)

# Firewall for security
firewall = hcloud.Firewall("medlitbot-firewall",
    name=f"medlitbot-{environment}-firewall",
    rules=[
        # SSH access
        hcloud.FirewallRuleArgs(
            direction="in",
            port="22",
            protocol="tcp",
            source_ips=["0.0.0.0/0", "::/0"]
        ),
        # HTTP access
        hcloud.FirewallRuleArgs(
            direction="in",
            port="80",
            protocol="tcp", 
            source_ips=["0.0.0.0/0", "::/0"]
        ),
        # HTTPS access
        hcloud.FirewallRuleArgs(
            direction="in",
            port="443",
            protocol="tcp",
            source_ips=["0.0.0.0/0", "::/0"]
        )
    ]
)

# Block storage for persistent data
volume = hcloud.Volume("medlitbot-storage",
    name=f"medlitbot-{environment}-storage",
    size=volume_size,
    location=server_location
)

# Cloud-init script for automated server setup
cloud_init_script = f"""#!/bin/bash
set -e

# Update system
apt-get update && apt-get upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker root

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install system dependencies
apt-get install -y git curl wget htop tree unzip nginx certbot python3-certbot-nginx

# Create mount point and mount volume
mkdir -p /mnt/medlitbot-data
echo "/dev/disk/by-id/scsi-0HC_Volume_$(echo {volume.id} | cut -d'-' -f2-) /mnt/medlitbot-data ext4 defaults 0 2" >> /etc/fstab

# Format volume if it's new (only on first boot)
if ! blkid /dev/disk/by-id/scsi-0HC_Volume_*; then
    mkfs.ext4 /dev/disk/by-id/scsi-0HC_Volume_*
fi

mount -a

# Create application directories
mkdir -p /mnt/medlitbot-data/app
mkdir -p /mnt/medlitbot-data/postgres
mkdir -p /mnt/medlitbot-data/redis
mkdir -p /mnt/medlitbot-data/media
mkdir -p /mnt/medlitbot-data/logs
mkdir -p /mnt/medlitbot-data/staticfiles

# Set proper permissions
chown -R 1000:1000 /mnt/medlitbot-data

# Create environment file
cat > /mnt/medlitbot-data/.env << 'EOF'
# Django Configuration
DEBUG=False
SECRET_KEY={django_secret_key}
ALLOWED_HOSTS={allowed_hosts}

# Database Configuration
DB_NAME=medlitbot
DB_USER=medlitbot
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
DB_HOST=postgres
DB_PORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# CORS Configuration
CORS_ALLOWED_ORIGINS=*

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE=104857600
DATA_UPLOAD_MAX_MEMORY_SIZE=104857600
EOF

# Clone application repository (placeholder - update with your repo)
cd /mnt/medlitbot-data
echo "Application repository should be cloned here during deployment"

# Signal that initialization is complete
touch /tmp/cloud-init-complete
"""

# Main server
server = hcloud.Server("medlitbot-server",
    name=f"medlitbot-{environment}",
    image="ubuntu-22.04",
    server_type=server_type,
    location=server_location,
    ssh_keys=[ssh_key.id],
    firewall_ids=[firewall.id],
    user_data=base64.b64encode(cloud_init_script.encode()).decode(),
    volumes=[volume.id]
)

# Network configuration
network = hcloud.Network("medlitbot-network",
    name=f"medlitbot-{environment}-network",
    ip_range="10.0.0.0/16"
)

network_subnet = hcloud.NetworkSubnet("medlitbot-subnet",
    network_id=network.id,
    type="cloud",
    network_zone="eu-central",
    ip_range="10.0.1.0/24"
)

# Attach server to network
server_network = hcloud.ServerNetwork("medlitbot-server-network",
    server_id=server.id,
    network_id=network.id,
    ip="10.0.1.10"
)

# Export important values
pulumi.export("server_id", server.id)
pulumi.export("server_public_ip", server.public_net.ipv4.ip)
pulumi.export("server_private_ip", server_network.ip)
pulumi.export("volume_id", volume.id)
pulumi.export("ssh_connection", Output.format("ssh root@{0}", server.public_net.ipv4.ip))
pulumi.export("application_url", Output.format("http://{0}", server.public_net.ipv4.ip))
pulumi.export("environment", environment)

# Cost estimation output
pulumi.export("estimated_monthly_cost_eur", Output.format("""
Server ({0} ARM64): ~€3-4/month
Volume ({1}GB): ~€{2}/month  
Network: €0/month
Total: ~€{3}-{4}/month
""", server_type, volume_size, volume_size * 0.5, 3 + (volume_size * 0.5), 4 + (volume_size * 0.5)))
