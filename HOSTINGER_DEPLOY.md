# Hostinger Deployment Guide

## Step 1: Hostinger Setup
1. Login to Hostinger hPanel
2. Go to **Websites** → **Manage**
3. Go to **Advanced** → **SSH Access** → Enable SSH
4. Note your SSH credentials

## Step 2: Upload Files
1. Go to **File Manager** or use FTP
2. Navigate to `public_html` folder
3. Upload ALL project files

## Step 3: SSH Commands
Connect via SSH and run:

```bash
cd ~/domains/yourdomain.com/public_html

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install django requests beautifulsoup4 pillow

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

## Step 4: Update .htaccess
Edit `.htaccess` and replace:
- `u123456789` with your Hostinger username
- `yourdomain.com` with your actual domain

## Step 5: Update settings.py
Change these in `Sattapana/settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

## Step 6: Setup Cron Job (Auto-fetch every hour)
1. Go to hPanel → **Advanced** → **Cron Jobs**
2. Add new cron job:
   - Command: `cd ~/domains/yourdomain.com/public_html && ~/domains/yourdomain.com/public_html/venv/bin/python fetch_results.py`
   - Schedule: Every hour (0 * * * *)

## Step 7: Restart
Go to **Advanced** → **Python** → Restart application

## Troubleshooting
- Check error logs in hPanel
- Make sure all file permissions are correct (644 for files, 755 for folders)
- Ensure Python version is 3.8+

## Important Files
- `passenger_wsgi.py` - WSGI entry point
- `.htaccess` - Apache configuration
- `fetch_results.py` - Auto-fetch script
