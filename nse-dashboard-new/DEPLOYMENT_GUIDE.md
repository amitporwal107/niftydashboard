# 🚀 Self-Deployment Guide - NIFTY Options Dashboard

## Overview

This guide covers multiple deployment options for your Streamlit-based NIFTY Options Analysis Dashboard.

---

## 📦 Prerequisites

Your dashboard consists of:
- **Main App**: `/app/dashboard.py` (Streamlit)
- **Parser**: `/app/nse_option_chain.py` (Python script)
- **Data Folder**: `/app/nsedata/` (CSV storage)
- **Dependencies**: streamlit, plotly, pandas

---

## 🎯 Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free & Easy)

**Steps:**

1. **Push Code to GitHub**
   ```bash
   cd /app
   git init
   git add dashboard.py nse_option_chain.py nsedata/
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Create requirements.txt**
   ```bash
   cat > requirements.txt << EOF
streamlit==1.55.0
plotly==6.6.0
pandas==2.3.3
EOF
   ```

3. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `dashboard.py`
   - Click "Deploy"

**✅ Pros:**
- Free hosting
- Auto-updates on git push
- Built-in HTTPS
- Easy sharing

**❌ Cons:**
- Limited resources on free tier
- Public by default

---

### Option 2: Docker Deployment (Any Cloud Provider)

**Create Dockerfile:**

```dockerfile
# /app/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY dashboard.py .
COPY nse_option_chain.py .
COPY nsedata/ ./nsedata/

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

**Create requirements.txt:**
```bash
cat > /app/requirements.txt << 'EOF'
streamlit==1.55.0
plotly==6.6.0
pandas==2.3.3
EOF
```

**Build and Run:**
```bash
cd /app

# Build Docker image
docker build -t nifty-dashboard .

# Run container
docker run -d \
  -p 8501:8501 \
  -v $(pwd)/nsedata:/app/nsedata \
  --name nifty-dashboard \
  nifty-dashboard
```

**Access:** http://localhost:8501

---

### Option 3: AWS EC2 Deployment

**Steps:**

1. **Launch EC2 Instance**
   - OS: Ubuntu 22.04
   - Instance Type: t2.micro (free tier) or t2.small
   - Security Group: Open port 8501

2. **SSH into Instance**
   ```bash
   ssh -i your-key.pem ubuntu@<ec2-public-ip>
   ```

3. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv
   ```

4. **Upload Files**
   ```bash
   # From your local machine
   scp -i your-key.pem -r /app/dashboard.py ubuntu@<ec2-ip>:/home/ubuntu/
   scp -i your-key.pem -r /app/nse_option_chain.py ubuntu@<ec2-ip>:/home/ubuntu/
   scp -i your-key.pem -r /app/nsedata ubuntu@<ec2-ip>:/home/ubuntu/
   ```

5. **Setup on EC2**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install streamlit plotly pandas
   
   # Run with nohup
   nohup streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0 &
   ```

6. **Access:** http://<ec2-public-ip>:8501

**For Production:**
```bash
# Install supervisor for process management
sudo apt install supervisor

# Create config
sudo nano /etc/supervisor/conf.d/dashboard.conf
```

Add:
```ini
[program:streamlit-dashboard]
command=/home/ubuntu/venv/bin/streamlit run /home/ubuntu/dashboard.py --server.port=8501 --server.address=0.0.0.0
directory=/home/ubuntu
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/streamlit.err.log
stdout_logfile=/var/log/streamlit.out.log
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start streamlit-dashboard
```

---

### Option 4: Heroku Deployment

**Steps:**

1. **Create Heroku Files**

**Procfile:**
```bash
cat > /app/Procfile << 'EOF'
web: streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0
EOF
```

**runtime.txt:**
```bash
cat > /app/runtime.txt << 'EOF'
python-3.11.0
EOF
```

**requirements.txt:**
```bash
cat > /app/requirements.txt << 'EOF'
streamlit==1.55.0
plotly==6.6.0
pandas==2.3.3
EOF
```

2. **Deploy**
```bash
cd /app
heroku login
heroku create nifty-options-dashboard
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

3. **Access:** https://nifty-options-dashboard.herokuapp.com

---

### Option 5: DigitalOcean App Platform

**Steps:**

1. Push code to GitHub (see Option 1)
2. Go to DigitalOcean App Platform
3. Create new app from GitHub repo
4. Configure:
   - **Run Command**: `streamlit run dashboard.py --server.port=8080 --server.address=0.0.0.0`
   - **Port**: 8080
   - **Environment**: Python 3.11
5. Deploy

**Cost:** ~$5/month

---

### Option 6: Local/VPS with Nginx (Production Setup)

**1. Install Nginx**
```bash
sudo apt install nginx
```

**2. Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/streamlit
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # or IP address

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

**3. Enable Site**
```bash
sudo ln -s /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**4. Add SSL (Optional but Recommended)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🔒 Security Best Practices

1. **Add Authentication** (Streamlit-Authenticator)
```bash
pip install streamlit-authenticator
```

Add to dashboard.py:
```python
import streamlit_authenticator as stauth

# Authentication config
names = ['Admin']
usernames = ['admin']
passwords = ['your-hashed-password']

authenticator = stauth.Authenticate(names, usernames, passwords,
    'some_cookie_name', 'some_signature_key', cookie_expiry_days=30)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Your dashboard code here
    authenticator.logout('Logout', 'sidebar')
elif authentication_status == False:
    st.error('Username/password is incorrect')
```

2. **Environment Variables**
```bash
# Create .env file (don't commit this!)
cat > .env << 'EOF'
DATA_FOLDER=/app/nsedata
MAX_UPLOAD_SIZE=200
EOF
```

3. **Rate Limiting**
   - Use Nginx rate limiting
   - Or use Cloudflare (free tier)

---

## 📊 Monitoring

**Add to dashboard.py:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/dashboard.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🔄 Backup Strategy

**Automated Backup Script:**
```bash
#!/bin/bash
# /app/backup.sh

BACKUP_DIR="/backups/nsedata"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/nsedata_$DATE.tar.gz /app/nsedata/

# Keep only last 7 days
find $BACKUP_DIR -name "nsedata_*.tar.gz" -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /app/backup.sh
```

---

## 📋 Quick Deployment Checklist

- [ ] Choose deployment platform
- [ ] Create requirements.txt
- [ ] Test locally first
- [ ] Configure firewall/security groups
- [ ] Set up domain (optional)
- [ ] Configure SSL certificate
- [ ] Add authentication (recommended)
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test CSV upload functionality
- [ ] Document deployment for team

---

## 🆘 Troubleshooting

**Issue: Port already in use**
```bash
sudo lsof -i :8501
kill -9 <PID>
```

**Issue: Permission denied on data folder**
```bash
chmod 755 /app/nsedata
```

**Issue: Large CSV files failing**
- Increase Streamlit max upload size:
```python
# In dashboard.py
st.set_page_config(
    page_title="NIFTY Options",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add to .streamlit/config.toml
[server]
maxUploadSize = 200  # MB
```

---

## 💰 Cost Comparison

| Platform | Cost | Pros | Cons |
|----------|------|------|------|
| Streamlit Cloud | Free | Easy, auto-deploy | Limited resources |
| AWS EC2 (t2.micro) | Free (1 year) | Full control | Setup required |
| Heroku | $7/month | Easy deploy | Limited free tier |
| DigitalOcean | $5/month | Good performance | Manual setup |
| VPS (Hetzner) | €4/month | Cheap, powerful | Full management |

---

## 🎯 Recommended: Streamlit Cloud for Testing, AWS/DO for Production

**For Quick Testing:** Use Streamlit Cloud
**For Production:** Use AWS EC2 + Nginx + SSL or DigitalOcean

---

## 📞 Support

If you need help with deployment, check:
- Streamlit Docs: https://docs.streamlit.io/
- Docker Hub: https://hub.docker.com/
- DigitalOcean Tutorials: https://www.digitalocean.com/community/tutorials
