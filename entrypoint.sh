#!/bin/bash
set -e

export $(grep -v '^#' .env | xargs)

echo ">>> PostgreSQL ishga tushmoqda ..."
while ! nc -z db 5432; do
  sleep 0.5
done

echo ">>> PostgreSQL ishga tushdi ..."

echo ">>> Migratsiyalar qabul qilinmoqda ..."
python manage.py migrate --noinput

echo ">>> Static fayllar to'planmoqda ..."
python manage.py collectstatic --noinput

echo "Gunicorn ishga tushmoqda ..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$WEB_PORT \
    --workers=3 \
    --threads=3 \
    --worker-class=gthread \
    --timeout=120
