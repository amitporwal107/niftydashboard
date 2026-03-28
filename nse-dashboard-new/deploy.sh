#!/bin/bash

# NIFTY Options Dashboard - Quick Deployment Script
# This script helps you deploy the dashboard on a Linux server

set -e

echo "🚀 NIFTY Options Dashboard - Deployment Script"
echo "================================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "⚠️  Please don't run as root. Run as a regular user with sudo access."
   exit 1
fi

# Function to install dependencies
install_dependencies() {
    echo "📦 Installing system dependencies..."
    sudo apt update
    sudo apt install -y python3-pip python3-venv supervisor nginx
    echo "✅ System dependencies installed"
}

# Function to setup Python environment
setup_python_env() {
    echo "🐍 Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Python environment ready"
}

# Function to setup supervisor
setup_supervisor() {
    echo "⚙️  Configuring Supervisor..."
    
    CURRENT_DIR=$(pwd)
    VENV_PATH="$CURRENT_DIR/venv/bin/streamlit"
    
    sudo tee /etc/supervisor/conf.d/nifty-dashboard.conf > /dev/null <<EOF
[program:nifty-dashboard]
command=$VENV_PATH run $CURRENT_DIR/dashboard.py --server.port=8501 --server.address=0.0.0.0
directory=$CURRENT_DIR
user=$USER
autostart=true
autorestart=true
stderr_logfile=/var/log/nifty-dashboard.err.log
stdout_logfile=/var/log/nifty-dashboard.out.log
environment=PATH="$CURRENT_DIR/venv/bin"
EOF

    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl start nifty-dashboard
    
    echo "✅ Supervisor configured and dashboard started"
}

# Function to setup Nginx
setup_nginx() {
    echo "🌐 Configuring Nginx..."
    
    read -p "Enter your domain name (or press Enter for IP-based access): " DOMAIN
    
    if [ -z "$DOMAIN" ]; then
        DOMAIN="_"
    fi
    
    sudo tee /etc/nginx/sites-available/nifty-dashboard > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/nifty-dashboard /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx
    
    echo "✅ Nginx configured"
}

# Function to setup SSL
setup_ssl() {
    read -p "Do you want to setup SSL certificate? (y/n): " SETUP_SSL
    
    if [ "$SETUP_SSL" = "y" ]; then
        read -p "Enter your domain name: " DOMAIN
        
        if [ ! -z "$DOMAIN" ]; then
            sudo apt install -y certbot python3-certbot-nginx
            sudo certbot --nginx -d $DOMAIN
            echo "✅ SSL certificate installed"
        else
            echo "⚠️  Domain name required for SSL"
        fi
    fi
}

# Main deployment flow
main() {
    echo "Select deployment option:"
    echo "1) Full deployment (dependencies + supervisor + nginx)"
    echo "2) Quick start (just run with nohup)"
    echo "3) Docker deployment"
    read -p "Choose option (1-3): " OPTION
    
    case $OPTION in
        1)
            install_dependencies
            setup_python_env
            setup_supervisor
            setup_nginx
            setup_ssl
            echo ""
            echo "🎉 Deployment complete!"
            echo "📊 Dashboard running at: http://$(hostname -I | awk '{print $1}')"
            echo "📝 Logs: /var/log/nifty-dashboard.*.log"
            echo "🔧 Manage: sudo supervisorctl status nifty-dashboard"
            ;;
        2)
            setup_python_env
            echo "🚀 Starting dashboard..."
            source venv/bin/activate
            nohup streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0 > dashboard.log 2>&1 &
            echo "✅ Dashboard started in background"
            echo "📊 Access at: http://$(hostname -I | awk '{print $1}'):8501"
            echo "📝 Logs: tail -f dashboard.log"
            ;;
        3)
            echo "🐳 Building Docker image..."
            docker build -t nifty-dashboard .
            echo "🚀 Running container..."
            docker run -d \
                -p 8501:8501 \
                -v $(pwd)/nsedata:/app/nsedata \
                --name nifty-dashboard \
                --restart unless-stopped \
                nifty-dashboard
            echo "✅ Docker container running"
            echo "📊 Dashboard at: http://$(hostname -I | awk '{print $1}'):8501"
            echo "🔧 Manage: docker logs -f nifty-dashboard"
            ;;
        *)
            echo "Invalid option"
            exit 1
            ;;
    esac
}

# Run main function
main
