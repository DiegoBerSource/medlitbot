# 🚀 Quick Start: Deploy MedLitBot to Hetzner Cloud

Get your MedLitBot instance running on Hetzner Cloud in under 10 minutes with minimal cost (~€15/month).

## 📋 Prerequisites (5 minutes)

1. **Hetzner Cloud Account** 
   - Sign up at https://www.hetzner.com/cloud
   - Add payment method (€20 free credit for new accounts)

2. **Create API Token**
   - Go to Hetzner Console → Security → API tokens
   - Generate new token with Read & Write permissions
   - Copy the token (you'll need it soon)

3. **Install Tools**
   ```bash
   # Install Pulumi CLI
   curl -fsSL https://get.pulumi.com | sh
   
   # Restart terminal or run:
   export PATH=$PATH:$HOME/.pulumi/bin
   
   # Install Python dependencies
   cd infrastructure
   pip install -r requirements.txt
   ```

4. **Generate SSH Key** (if you don't have one)
   ```bash
   ssh-keygen -t rsa -b 4096 -C "medlitbot-deploy"
   # Press Enter for all prompts (use default location and no passphrase)
   ```

## ⚡ 5-Minute Deployment

### Step 1: Initialize Pulumi (1 minute)
```bash
cd infrastructure

# Login to Pulumi (free tier is fine)
pulumi login

# Create production stack
pulumi stack init prod
```

### Step 2: Configure Secrets (2 minutes)
```bash
# Hetzner API token (from step 2 above)
pulumi config set hcloud:token YOUR_HETZNER_API_TOKEN --secret

# SSH public key for server access
pulumi config set ssh_public_key "$(cat ~/.ssh/id_rsa.pub)"

# Generate Django secret key
pulumi config set django_secret_key "$(openssl rand -base64 50)" --secret

# Basic configuration
pulumi config set server_type cx11        # Minimal server
pulumi config set volume_size 20          # 20GB storage
pulumi config set allowed_hosts "*"       # Allow all hosts (change after domain setup)
```

### Step 3: Deploy! (2 minutes)
```bash
# Deploy infrastructure and application
python deploy.py
```

That's it! 🎉 Your application will be available at the IP address shown in the output.

## 🔗 Access Your Application

After deployment completes, you'll see:
```
🎉 Deployment complete!

📝 Server Details:
   - Public IP: 123.456.789.012
   - SSH Access: ssh root@123.456.789.012
   - Application URL: http://123.456.789.012
```

### First Steps:
1. **Visit the app**: Open `http://YOUR_SERVER_IP` in your browser
2. **Admin access**: Go to `http://YOUR_SERVER_IP/admin/`
   - Username: `admin`
   - Password: `adminpass123` (⚠️ Change this immediately!)
3. **API docs**: Check `http://YOUR_SERVER_IP/api/docs`

## 🏠 Custom Domain Setup (Optional)

### Point Domain to Server
1. In your domain registrar (GoDaddy, Namecheap, etc.):
   - Create A record: `yourdomain.com` → `YOUR_SERVER_IP`
   - Create A record: `www.yourdomain.com` → `YOUR_SERVER_IP`

2. Update configuration:
   ```bash
   pulumi config set allowed_hosts "yourdomain.com,www.yourdomain.com"
   pulumi config set domain_name "yourdomain.com"
   pulumi up
   ```

3. Setup SSL certificate:
   ```bash
   ssh root@YOUR_SERVER_IP
   certbot --nginx -d yourdomain.com -d www.yourdomain.com --non-interactive --agree-tos --email your@email.com
   ```

## 💰 Cost Breakdown

**Monthly Costs (€):**
- CX11 Server (1 vCPU, 4GB RAM): €4.90
- 20GB Block Storage: €10.00
- Network traffic: €0.00 (20TB included)
- **Total: ~€15/month**

## 🔧 Common Tasks

### View Application Logs
```bash
ssh root@YOUR_SERVER_IP "cd /mnt/medlitbot-data/app && docker-compose -f docker-compose.prod.yml logs -f web"
```

### Update Application
```bash
cd infrastructure
python deploy.py  # Automatically pulls latest code and redeploys
```

### Scale Up Server
```bash
pulumi config set server_type cx21  # 2 vCPU, 8GB RAM (+€4/month)
pulumi up
```

### Add More Storage
```bash
pulumi config set volume_size 50    # 50GB (+€15/month)
pulumi up
```

## 🆘 Troubleshooting

### Can't Connect to Server?
- Wait 2-3 minutes for server initialization
- Check firewall: `pulumi stack output` shows all details

### Application Not Loading?
```bash
# Check if services are running
ssh root@YOUR_SERVER_IP "cd /mnt/medlitbot-data/app && docker-compose -f docker-compose.prod.yml ps"

# View error logs
ssh root@YOUR_SERVER_IP "cd /mnt/medlitbot-data/app && docker-compose -f docker-compose.prod.yml logs web"
```

### Out of Memory?
- Upgrade to cx21: `pulumi config set server_type cx21 && pulumi up`
- Or optimize containers: reduce Celery workers in docker-compose.prod.yml

## 🗑️ Clean Up

To destroy everything and stop billing:
```bash
cd infrastructure
pulumi destroy  # Removes all resources
```

## 📚 Next Steps

- ✅ **Security**: Change admin password immediately
- ✅ **Monitoring**: Set up UptimeRobot or similar
- ✅ **Backups**: Implement database backup strategy  
- ✅ **Domain**: Point your domain and setup SSL
- ✅ **Scale**: Monitor usage and upgrade resources as needed

## 🤝 Need Help?

- **Infrastructure issues**: Check `infrastructure/README.md` for detailed docs
- **Application issues**: Check Django logs and API documentation
- **Hetzner issues**: Check Hetzner Cloud Console for server status

---

**🎯 Goal achieved**: Full-featured medical AI platform running on cloud infrastructure for the price of a few cups of coffee per month!
