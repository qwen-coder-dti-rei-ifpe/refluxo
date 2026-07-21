#!/bin/bash
set -e

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Setup environment
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Database migrations
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Populate mock data (ignore errors if data already exists)
python manage.py popular_dados_mock --noinput || echo 'Aviso: Não foi possível executar popular_dados_mock - dados podem já existir'

# Collect static files
python manage.py collectstatic --noinput
