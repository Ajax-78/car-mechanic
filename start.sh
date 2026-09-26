cat << 'EOF' > start.sh
#!/usr/bin/env bash
set -e

echo "Applying Database Migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn Server..."
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
EOF