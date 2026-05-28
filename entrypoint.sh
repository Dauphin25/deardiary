#!/bin/sh
set -e

echo "Applying database migrations..."
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "Installing Playwright browsers..."
playwright install chromium

echo "Starting server..."
exec gunicorn DiaryProject.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
