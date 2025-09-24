# Django Migration Issues - Complete Solution Guide

## Problem Description
You're encountering Django migration issues when trying to add non-nullable foreign key fields (`organization`) to existing models. This is a common issue when modifying models that already have data.

## Root Cause
Django cannot add a non-nullable field to a table that already has rows because it doesn't know what value to assign to existing rows for the new field.

## Complete Solution

### Step 1: Clean Migration State (if needed)
If you have migration conflicts, reset the migration state:

```bash
# Remove migration files (keep __init__.py)
rm voucher_system/migrations/0*.py

# Remove database (if using SQLite for development)
rm db.sqlite3

# Create fresh migrations
python3 manage.py makemigrations voucher_system
python3 manage.py migrate
```

### Step 2: Use the Provided Migration Strategy

The models I've created use a three-step migration approach:

1. **Initial Migration**: Creates models with nullable organization fields
2. **Data Migration**: Creates default organization and assigns it to existing records
3. **Schema Migration**: Makes organization fields non-nullable

### Step 3: Apply Migrations in Sequence

```bash
# Apply all migrations
python3 manage.py migrate voucher_system

# Setup sample data
python3 manage.py setup_erp

# Create superuser
python3 manage.py createsuperuser
```

### Step 4: Alternative Manual Approach

If you encounter the prompts you mentioned, here's how to handle them:

#### For the timezone.now prompt:
```
[default: timezone.now] >>> timezone.now
```
Just press Enter to accept the default.

#### For the organization field prompt:
```
Select an option: 1
>>> 1
```
Choose option 1 to provide a one-off default.

#### For created_at field with auto_now_add:
```
Select an option: 1
>>> timezone.now
```
Choose option 1 and enter `timezone.now`.

### Step 5: Quick Setup (Recommended)

Use the provided quick setup script:

```bash
./quick_setup.sh
```

This script will:
1. Apply all migrations
2. Create sample data
3. Prompt you to create a superuser
4. Give you next steps

## Model Design Features

The models I've created include:

### 1. Migration-Safe Design
- Initial nullable foreign keys
- Data migration to populate defaults
- Final migration to make fields required

### 2. Comprehensive Field Support
- JSON fields for schema storage
- UDF (User-Defined Fields) support
- Validation rules storage
- Audit fields (created_at, updated_at, created_by)

### 3. Business Logic
- Organization-based multi-tenancy
- Flexible voucher configurations
- Dynamic form generation support

## Testing the Setup

After running the setup:

1. **Access Admin**: http://127.0.0.1:8000/admin/
2. **Check Models**: Verify all models are created
3. **Sample Data**: Confirm sample organizations and voucher configs exist
4. **UDF Support**: Test adding user-defined fields

## Common Issues and Solutions

### Issue 1: "externally-managed-environment"
```bash
# Use virtual environment
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

### Issue 2: Migration conflicts
```bash
# Reset migrations
python3 manage.py migrate voucher_system zero
python3 manage.py makemigrations voucher_system
python3 manage.py migrate
```

### Issue 3: Missing dependencies
```bash
# Install with --break-system-packages if needed
pip install --break-system-packages Django PyYAML
```

## File Structure Created

```
erp_project/
├── manage.py
├── requirements.txt
├── quick_setup.sh
├── fix_migrations.py
├── MIGRATION_FIX_GUIDE.md
├── erp_project/
│   ├── settings.py
│   └── ...
└── voucher_system/
    ├── models.py
    ├── admin.py
    ├── schema_loader.py
    ├── migrations/
    │   ├── 0001_initial.py
    │   ├── 0002_add_default_organization.py
    │   └── 0003_make_organization_required.py
    └── management/
        └── commands/
            └── setup_erp.py
```

## Next Steps

1. **Run Quick Setup**: `./quick_setup.sh`
2. **Start Server**: `python3 manage.py runserver`
3. **Access Admin**: Create voucher configurations and UDFs
4. **Build Forms**: Use the schema system to create dynamic forms

This solution provides a complete, production-ready foundation for your dynamic voucher entry system while properly handling Django migration constraints.