#!/usr/bin/env python
"""
Railway deployment script
This script is run during deployment to set up the database and create admin user
"""
import os
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vanity_project.settings')
    django.setup()
    
    from django.contrib.auth.models import User
    
    # Create superuser if it doesn't exist
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("Created admin user: admin/admin123")
    else:
        print("Admin user already exists")