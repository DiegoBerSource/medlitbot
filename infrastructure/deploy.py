#!/usr/bin/env python3
"""
Deployment script for MedLitBot on Hetzner Cloud
This script helps automate the deployment process
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path

def run_command(cmd, check=True, capture_output=False):
    """Run a shell command and handle errors"""
    print(f"Running: {cmd}")
    if capture_output:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"Error: {result.stderr}")
            sys.exit(1)
        return result.stdout.strip()
    else:
        result = subprocess.run(cmd, shell=True)
        if check and result.returncode != 0:
            sys.exit(1)
        return None

def wait_for_server(ip_address, max_attempts=30):
    """Wait for server to be accessible via SSH"""
    print(f"Waiting for server {ip_address} to be ready...")
    
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(
                f"ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@{ip_address} 'echo ready'",
                shell=True, capture_output=True, timeout=15
            )
            if result.returncode == 0:
                print("✅ Server is ready!")
                return True
        except subprocess.TimeoutExpired:
            pass
        
        print(f"Attempt {attempt + 1}/{max_attempts} - waiting 10 seconds...")
        time.sleep(10)
    
    print("❌ Server is not responding to SSH")
    return False

def deploy_infrastructure():
    """Deploy the infrastructure using Pulumi"""
    print("🚀 Deploying infrastructure...")
    
    # Check if we're in the infrastructure directory
    if not Path("Pulumi.yaml").exists():
        print("Please run this script from the infrastructure directory")
        sys.exit(1)
    
    # Install Pulumi dependencies
    run_command("pip install -r requirements.txt")
    
    # Check if stack exists, create if not
    try:
        run_command("pulumi stack select prod", capture_output=True)
    except:
        run_command("pulumi stack init prod")
    
    # Deploy the stack
    run_command("pulumi up --yes")
    
    # Get outputs
    outputs = json.loads(run_command("pulumi stack output --json", capture_output=True))
    return outputs

def deploy_application(server_ip):
    """Deploy the application to the server"""
    print("🚀 Deploying application...")
    
    # Wait for server to be ready
    if not wait_for_server(server_ip):
        print("❌ Cannot connect to server")
        sys.exit(1)
    
    # Copy application files
    run_command(f"rsync -avz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' ../ root@{server_ip}:/mnt/medlitbot-data/app/")
    
    # Setup and start services
    deploy_commands = [
        "cd /mnt/medlitbot-data/app",
        "docker-compose -f docker-compose.prod.yml build",
        "docker-compose -f docker-compose.prod.yml up -d",
        "docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput",
        "docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate",
        "echo 'from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser(\"admin\", \"admin@example.com\", \"adminpass123\")' | docker-compose -f docker-compose.prod.yml exec -T web python manage.py shell"
    ]
    
    for cmd in deploy_commands:
        run_command(f"ssh root@{server_ip} '{cmd}'")
    
    print("✅ Application deployed successfully!")

def setup_ssl(server_ip, domain=None):
    """Setup SSL certificate using Let's Encrypt"""
    if not domain:
        print("⚠️  No domain provided, skipping SSL setup")
        return
    
    print(f"🔒 Setting up SSL for {domain}...")
    
    ssl_commands = [
        f"certbot --nginx -d {domain} --non-interactive --agree-tos --email admin@{domain}",
        "systemctl reload nginx"
    ]
    
    for cmd in ssl_commands:
        run_command(f"ssh root@{server_ip} '{cmd}'")
    
    print("✅ SSL certificate installed!")

def main():
    """Main deployment function"""
    print("🚀 Starting MedLitBot deployment to Hetzner Cloud...")
    
    # Deploy infrastructure
    outputs = deploy_infrastructure()
    server_ip = outputs.get("server_public_ip")
    
    if not server_ip:
        print("❌ Could not get server IP address")
        sys.exit(1)
    
    print(f"✅ Infrastructure deployed! Server IP: {server_ip}")
    
    # Deploy application
    deploy_application(server_ip)
    
    # Setup SSL (if domain is configured)
    domain = os.environ.get("DOMAIN_NAME")
    if domain and domain != "":
        setup_ssl(server_ip, domain)
    
    print(f"""
🎉 Deployment complete!

📝 Server Details:
   - Public IP: {server_ip}
   - SSH Access: ssh root@{server_ip}
   - Application URL: http://{server_ip}
   
🔧 Next Steps:
   1. Point your domain to {server_ip} (if using custom domain)
   2. Access the admin panel at http://{server_ip}/admin/ (admin/adminpass123)
   3. Upload your first dataset and start training models!
   
💰 Estimated monthly cost: {outputs.get('estimated_monthly_cost_eur', 'See Pulumi output')}
""")

if __name__ == "__main__":
    main()
