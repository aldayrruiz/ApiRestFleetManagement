#!/bin/bash

# Collect static files
#echo "Collect static files"
#python manage.py collectstatic --noinput

# Install postgres
echo "Installing postgres pip library"
pip install psycopg2

# Apply database migrations
echo "Apply database migrations"
python manage.py makemigrations
python manage.py migrate

# Creating tenant and admin
echo "Creating tenant Bilbao and admin as admin@admin.com with password password"
python manage.py createsuperuser2 --email admin@admin.com --fullname Admin --tenant Bilbao --password password

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000

