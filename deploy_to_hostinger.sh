#!/bin/bash
# Hostinger Deployment Script
# Run this after SSH: ssh root@72.61.238.249

echo "==================================="
echo "Hostinger Deployment Script"
echo "==================================="

# Navigate to project directory
cd ~/public_html || cd ~/domains/*/public_html

echo "Step 1: Pulling latest changes..."
# If using git, uncomment:
# git pull origin main

echo "Step 2: Activating virtual environment..."
source venv/bin/activate

echo "Step 3: Installing/Updating dependencies..."
pip install --upgrade django requests beautifulsoup4 pillow

echo "Step 4: Running migrations..."
python manage.py migrate

echo "Step 5: Collecting static files..."
python manage.py collectstatic --noinput

echo "Step 6: Setting permissions..."
chmod 664 db.sqlite3
chmod 755 .
chmod -R 755 media/

echo "Step 7: Testing fetch script..."
python fetch_results.py

echo "==================================="
echo "Deployment Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Visit your website to verify"
echo "2. Check admin panel: /admin-panel/"
echo "3. Verify cron job is running"
echo ""
