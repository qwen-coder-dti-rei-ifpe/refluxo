#!/bin/bash

# Change to the project directory where manage.py is located
cd ifpe_mvp

# Vercel handles virtual environment automatically
cp .env.example .env
echo "Building the project..."
python -m pip install -r requirements.txt

echo "Make Migration..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Collect Static..."
python manage.py collectstatic --noinput --clear
