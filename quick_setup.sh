#!/bin/bash

echo "ERP System Quick Setup Script"
echo "============================="

# Apply migrations
echo "Applying migrations..."
python3 manage.py migrate

# Setup sample data
echo "Setting up sample data..."
python3 manage.py setup_erp

# Create superuser
echo "Creating superuser..."
echo "Please create a superuser account:"
python3 manage.py createsuperuser

echo ""
echo "Setup completed successfully!"
echo ""
echo "To start the development server, run:"
echo "python3 manage.py runserver"
echo ""
echo "Then visit:"
echo "- Admin interface: http://127.0.0.1:8000/admin/"
echo "- Application: http://127.0.0.1:8000/"