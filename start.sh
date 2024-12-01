#!/bin/bash


wait-for-it db:5432 -t 10

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate


echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000 &

echo "Waiting for server to be ready..."
wait-for-it localhost:8000 --timeout=30 --strict -- echo "Server is ready, starting bot..."

# После того как сервер будет доступен, запускаем бота
echo "Starting bot..."
python manage.py bot
