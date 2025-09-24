#!/usr/bin/env python3
"""
Script to help resolve Django migration issues for the ERP system.
Run this script to properly handle migrations with foreign key constraints.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_project.settings')
django.setup()

from django.db import connection
from voucher_system.models import Organization, VoucherModeConfig, VoucherUDFConfig, Journal

def check_database_state():
    """Check current database state"""
    print("Checking database state...")
    
    with connection.cursor() as cursor:
        # Check if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'voucher_system_%';
        """)
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} voucher_system tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        if tables:
            # Check organization table
            try:
                cursor.execute("SELECT COUNT(*) FROM voucher_system_organization")
                org_count = cursor.fetchone()[0]
                print(f"Organizations in database: {org_count}")
            except:
                print("Organization table not accessible")

def create_default_data():
    """Create default organization and sample data"""
    print("\nCreating default data...")
    
    # Create default organization
    org, created = Organization.objects.get_or_create(
        code='DEFAULT',
        defaults={'name': 'Default Organization'}
    )
    
    if created:
        print(f"Created default organization: {org}")
    else:
        print(f"Using existing organization: {org}")
    
    # Update any existing records without organization
    updated_configs = VoucherModeConfig.objects.filter(organization__isnull=True).update(organization=org)
    updated_udfs = VoucherUDFConfig.objects.filter(organization__isnull=True).update(organization=org)
    updated_journals = Journal.objects.filter(organization__isnull=True).update(organization=org)
    
    print(f"Updated {updated_configs} VoucherModeConfig records")
    print(f"Updated {updated_udfs} VoucherUDFConfig records")
    print(f"Updated {updated_journals} Journal records")

def main():
    print("ERP System Migration Fix Script")
    print("=" * 40)
    
    # Check current state
    check_database_state()
    
    # Apply migrations
    print("\nApplying migrations...")
    execute_from_command_line(['manage.py', 'migrate', 'voucher_system'])
    
    # Create default data
    create_default_data()
    
    print("\nMigration fix completed successfully!")
    print("\nNext steps:")
    print("1. Run: python3 manage.py createsuperuser")
    print("2. Run: python3 manage.py runserver")
    print("3. Access admin at: http://127.0.0.1:8000/admin/")

if __name__ == '__main__':
    main()