# TechShop - Complete Installation Guide

A full-featured Django e-commerce platform with multi-level admin dashboards, inventory management, shopping cart, product compare, and modern shopping experience.

## Table of Contents
- [System Requirements](#system-requirements)
- [Quick Start (Windows)](#quick-start-windows)
- [Quick Start (Linux/Ubuntu)](#quick-start-linuxubuntu)
- [Quick Start (macOS)](#quick-start-macos)
- [Production Server Setup](#production-server-setup)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **Python**: 3.11 or higher
- **Operating System**: Windows 10+, Ubuntu 20.04+, macOS 12+
- **RAM**: 4GB (8GB recommended)
- **Disk Space**: 2GB free

### For Production
- **Database**: PostgreSQL 14+ (recommended) or MySQL 8+
- **Web Server**: Nginx
- **WSGI Server**: Gunicorn
- **SSL Certificate**: Let's Encrypt (free)

---

## Quick Start (Windows)

### Step 1: Install Python
1. Download Python 3.11+ from https://www.python.org/downloads/
2. Run the installer
3. **Important**: Check "Add Python to PATH"
4. Verify installation:
```cmd
python --version
```

### Step 2: Clone the Project
```cmd
git clone https://github.com/MeTariqul/MeTariqul-tecshop.git
cd MeTariqul-tecshop
```

### Step 3: Create Virtual Environment
```cmd
python -m venv venv
```

### Step 4: Activate Virtual Environment
```cmd
venv\Scripts\activate
```

### Step 5: Install Dependencies
```cmd
pip install -r requirements.txt
```

### Step 6: Configure Environment
1. Copy the example env file:
```cmd
copy .env.example techshop\.env
```
2. Edit `techshop\.env` with your settings (see Configuration section)

### Step 7: Run Migrations
```cmd
cd techshop
python manage.py migrate
```

### Step 8: Create Superuser
```cmd
python manage.py createsuperuser
```
Follow the prompts to create admin account.

### Step 9: Run Development Server
```cmd
python manage.py runserver
```

### Step 10: Access the Site
- **Storefront**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Store API**: http://127.0.0.1:8000/store/

---

## Quick Start (Linux/Ubuntu)

### Step 1: Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Python & Dependencies
```bash
sudo apt install python3 python3-pip python3-venv git -y
```

### Step 3: Clone the Project
```bash
git clone https://github.com/MeTariqul/MeTariqul-tecshop.git
cd MeTariqul-tecshop
```

### Step 4: Create Virtual Environment
```bash
python3 -m venv venv
```

### Step 5: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 6: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 7: Configure Environment
```bash
cp .env.example techshop/.env
nano techshop/.env
```

### Step 8: Run Migrations
```bash
cd techshop
python manage.py migrate
```

### Step 9: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 10: Run Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

### Step 11: Access the Site
- **Storefront**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/

---

## Quick Start (macOS)

### Step 1: Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

### Step 2: Install Python
```bash
brew install python@3.11
```

### Step 3: Clone and Setup
```bash
git clone https://github.com/MeTariqul/MeTariqul-tecshop.git
cd MeTariqul-tecshop
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Configure and Run
```bash
cp .env.example techshop/.env
cd techshop
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Production Server Setup

### Option 1: DigitalOcean Droplet

#### 1. Create Droplet
- Choose: Ubuntu 22.04 LTS
- Size: $20/month (2GB RAM, 80GB SSD)
- Add SSH key

#### 2. Connect via SSH
```bash
ssh root@your_server_ip
```

#### 3. Follow Linux Installation Steps Above

#### 4. Install PostgreSQL
```bash
sudo apt install postgresql postgresql-contrib -y
sudo su - postgres
psql
CREATE DATABASE techshop_db;
CREATE USER techshop_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE techshop_db TO techshop_user;
\q
exit
```

#### 5. Update .env for PostgreSQL
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=techshop_db
DB_USER=techshop_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

#### 6. Install Gunicorn & Nginx
```bash
pip install gunicorn
sudo apt install nginx -y
```

#### 7. Create Gunicorn Service
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Add:
```
[Unit]
Description=Gunicorn instance for TechShop
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/root/MeTariqul-tecshop/techshop
ExecStart=/root/MeTariqul-tecshop/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 techshop.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

#### 8. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/techshop
```

Add:
```nginx
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /root/MeTariqul-tecshop techshop/static/;
    }

    location /media/ {
        alias /root/MeTariqul-tecshop/techshop/media/;
    }
}
```

#### 9. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/techshop /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
```

---

### Option 2: Railway (Easiest)

1. Go to https://railway.app/
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your forked repo
5. Add environment variables in Railway dashboard:
   - `SECRET_KEY`: Generate using `python -c "import secrets; print(secrets.token_hex(32))"`
   - `DEBUG`: False
   - `ALLOWED_HOSTS`: Your domain
   - `DB_ENGINE`: django.db.backends.postgresql
   - `DB_NAME`: Create in Railway dashboard (PostgreSQL plugin)
   - `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: From Railway PostgreSQL plugin
6. Add "Start Command" in settings: `cd techshop && python manage.py migrate && gunicorn techshop.wsgi:application`
7. Deploy!

---

### Option 3: Render.com

1. Go to https://render.com/
2. Sign up with GitHub
3. Create "Web Service"
4. Connect your GitHub repo
5. Configure:
   - Build Command: `pip install -r requirements.txt && python techshop/manage.py migrate`
   - Start Command: `gunicorn techshop.wsgi:application`
6. Add environment variables
7. Add PostgreSQL database (Render dashboard → Create Database)

---

## Configuration

### Environment Variables

Create `techshop/.env`:

```env
# Required
SECRET_KEY=your-secret-key-generate-with-python
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database (PostgreSQL recommended for production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=techshop_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Email (for order notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment (Stripe - optional)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### Generate Secret Key
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Troubleshooting

### Common Issues

#### 1. Migration Errors
```bash
# Reset database (development only!)
python manage.py migrate --fake-initial
```

#### 2. Static Files Not Loading
```bash
python manage.py collectstatic
```

#### 3. Permission Errors (Linux)
```bash
sudo chown -R www-data:www-data /path/to/project
```

#### 4. Database Connection Errors
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify credentials in .env
- Check firewall: `sudo ufw allow 5432`

#### 5. Email Not Sending
- For Gmail: Use App Password (not regular password)
- Enable 2-Factor Authentication → App Passwords

#### 6. Static Files 404 (Production)
- Ensure Nginx alias paths are correct
- Check collectstatic was run
- Verify MEDIA_ROOT and STATIC_ROOT in settings

---

## Features Overview

### Customer Features
- Product browsing with categories
- Shopping cart with persistence
- Coupon codes: SAVE10, SAVE20, WELCOME, FLAT50, FLAT100
- Save for Later
- Product Compare (up to 4 products)
- Wishlist
- Checkout with multiple payment options
- Order tracking
- PDF invoice download

### Admin Features
- Multi-level dashboard (Director, Manager, Warehouse, Fulfillment)
- Product management
- Inventory tracking
- Order management
- Customer support system
- Staff management with roles
- Reports and analytics

---

## Admin Login

After creating superuser:
1. Go to `/admin/`
2. Login with your credentials
3. Access dashboards:
   - Main: `/admin-dashboard/`
   - Director: `/admin-dashboard/director/`
   - Warehouse: `/admin-dashboard/warehouse/`
   - Fulfillment: `/admin-dashboard/fulfillment/`

---

## Support

For issues or questions:
- Create an issue on GitHub
- Check Django documentation: https://docs.djangoproject.com/

---

## License

MIT License - See LICENSE file for details.

---

⭐ Star this repo if you found it helpful!
