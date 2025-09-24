# ERP System - Dynamic Voucher Entry

A comprehensive Django-based ERP system with dynamic form generation capabilities, similar to enterprise systems like SAP or Microsoft Dynamics NAV.

## 🚀 Quick Start

### 1. Migration Issues - SOLVED ✅

If you encounter the migration issues you mentioned, here's the complete solution:

```bash
# Clean setup (if needed)
rm -rf voucher_system/migrations/0*.py
rm db.sqlite3

# Apply migrations in the correct order
python3 manage.py makemigrations voucher_system
python3 manage.py migrate

# Setup sample data
python3 manage.py setup_erp

# Create admin user
python3 manage.py createsuperuser

# Start server
python3 manage.py runserver
```

### 2. Alternative Quick Setup

```bash
./quick_setup.sh
```

## 🎯 Key Features

### ✨ Dynamic Form Generation
- **Schema-Driven**: Forms generated from JSON/YAML configurations
- **Runtime Configuration**: Add/modify fields without code changes
- **Multiple Layouts**: Standard, compact, detailed form styles
- **Validation Rules**: Schema-based field validation

### 🔧 User-Defined Fields (UDF)
- **No Code Changes**: Add custom fields through admin interface
- **Multiple Types**: Text, number, date, select, checkbox, etc.
- **Conditional Logic**: Show/hide fields based on other inputs
- **Validation**: Custom patterns, min/max values, required fields

### 🏢 Enterprise Features
- **Multi-Tenant**: Organization-based data separation
- **Audit Trail**: Created/updated timestamps and user tracking
- **Business Rules**: Configurable validation logic
- **API Endpoints**: JSON schema preview and configuration

## 📁 Project Structure

```
erp_project/
├── manage.py
├── requirements.txt
├── quick_setup.sh
├── fix_migrations.py
├── MIGRATION_FIX_GUIDE.md
├── README.md
├── erp_project/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── voucher_system/
│   ├── models.py              # Core data models
│   ├── admin.py               # Admin interface
│   ├── views.py               # Web views
│   ├── urls.py                # URL routing
│   ├── schema_loader.py       # Schema loading system
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_add_default_organization.py
│   │   └── 0003_make_organization_required.py
│   └── management/
│       └── commands/
│           └── setup_erp.py
└── templates/
    ├── base.html
    └── voucher_system/
        ├── home.html
        ├── config_detail.html
        └── test_form.html
```

## 🗃️ Database Models

### Core Models
- **Organization**: Multi-tenant organization management
- **JournalType**: Voucher categorization
- **VoucherModeConfig**: Main configuration with JSON schema
- **VoucherUDFConfig**: User-defined field configurations
- **Journal**: Main voucher entries
- **JournalLine**: Journal line items

### Key Features
- **JSON Schema Storage**: Flexible form definitions
- **UDF Support**: Custom fields without schema changes
- **Audit Fields**: Complete change tracking
- **Business Logic**: Validation rules and defaults

## 🎨 User Interface

### 1. Home Page (`/`)
- Lists all available voucher configurations
- Shows configuration details and UDF counts
- Quick access to schema viewing and form testing

### 2. Configuration Detail (`/config/{id}/`)
- Displays merged schema with UDF fields
- Shows raw JSON schema
- Field-by-field breakdown with types and requirements

### 3. Form Test (`/config/{id}/test/`)
- Demonstrates dynamic form generation
- Shows how fields would appear in actual forms
- Interactive demo of the form building process

### 4. Admin Interface (`/admin/`)
- Complete CRUD for all models
- UDF configuration interface
- Schema editing capabilities

## 🔧 Technical Implementation

### Schema Loading System
```python
# Load and merge schemas from multiple sources
loader = SchemaLoader()
schema = loader.get_merged_schema(voucher_config)

# Schema sources (in priority order):
# 1. Database ui_schema field
# 2. YAML files (config-specific)
# 3. Default schema template
# 4. UDF configurations
```

### Dynamic Form Building
```python
# Generate Django forms from schema
form_builder = FormBuilder(schema)
header_form = form_builder.build_header_form(Journal)
line_formset = form_builder.build_line_formset(JournalLine)
```

### UDF Integration
```python
# UDF fields are seamlessly integrated into schema
# Stored as JSON in database
# Supports validation, choices, conditional logic
udf_values = {
    'receipt_mode': 'cash',
    'customer_type': 'regular'
}
```

## 🔄 Migration Solution

### The Problem
Adding non-nullable foreign key fields to existing models causes Django migration issues.

### The Solution
Three-step migration approach:

1. **Initial Migration**: Creates models with nullable organization fields
2. **Data Migration**: Creates default organization and populates existing records
3. **Schema Migration**: Makes organization fields non-nullable

### Handling Migration Prompts

When Django asks for defaults:

```bash
# For timezone.now prompts:
[default: timezone.now] >>> timezone.now

# For organization field:
Select an option: 1
>>> 1

# For created_at with auto_now_add:
Select an option: 1
>>> timezone.now
```

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install Django PyYAML python-dateutil
# OR
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python3 manage.py migrate
```

### 3. Setup Sample Data
```bash
python3 manage.py setup_erp
```

### 4. Create Admin User
```bash
python3 manage.py createsuperuser
```

### 5. Start Server
```bash
python3 manage.py runserver
```

### 6. Access Application
- **Home**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

## 📊 Sample Data

The setup creates:

### Organizations
- Demo Organization (DEFAULT)

### Journal Types
- Cash Receipt
- Bank Payment
- General Journal
- Purchase Entry
- Sales Entry

### Voucher Configurations
- **Cash Receipt Voucher**: With UDF for receipt mode
- **Payment Voucher**: With pay-to field
- **General Journal**: Standard configuration

### UDF Example
- **Receipt Mode**: Select field with options (Cash, Cheque, Online Transfer)

## 🎯 Use Cases

### 1. Standard Voucher Entry
- Use pre-configured voucher types
- Standard fields with validation
- Multi-line journal entries

### 2. Custom Field Addition
- Add UDFs through admin interface
- No code deployment required
- Immediate availability in forms

### 3. Organization Customization
- Different configurations per organization
- Isolated data and settings
- Custom validation rules

### 4. Schema Evolution
- Modify field properties
- Add/remove fields dynamically
- Version-controlled changes

## 🔍 API Endpoints

### Schema Preview
```bash
GET /api/schema/{config_id}/
```

Returns merged schema with UDF fields:
```json
{
  "config": {
    "id": 1,
    "name": "Cash Receipt Voucher",
    "code": "CASH_RECEIPT"
  },
  "schema": {
    "header": {
      "date": {"type": "date", "required": true},
      "udf_receipt_mode": {"type": "select", "choices": {...}}
    },
    "lines": {...}
  }
}
```

## 🛠️ Customization

### Adding New Field Types
Extend the `FormBuilder` class:
```python
def get_field_class_and_widget(self, field_config):
    field_mapping = {
        'custom_type': (CustomField, CustomWidget),
        # ... existing mappings
    }
```

### Custom Validation Rules
Add to `VoucherModeConfig.validation_rules`:
```json
{
  "balance_check": "total_debit == total_credit",
  "date_range": "date >= start_date AND date <= end_date"
}
```

### Schema Files
Create YAML schemas in `voucher_system/schemas/`:
```yaml
# payment.yml
header:
  pay_to:
    type: text
    label: "Pay To"
    required: true
    max_length: 200
```

## 📈 Scalability Features

- **Database-Driven**: All configurations stored in database
- **JSON Schema**: Flexible field definitions
- **Multi-Tenant**: Organization separation
- **Caching Ready**: Schema loading optimized for caching
- **API First**: RESTful endpoints for integration

## 🔒 Security Considerations

- **Organization Isolation**: Data separated by organization
- **User Permissions**: Django's built-in auth system
- **Audit Trail**: Complete change tracking
- **Input Validation**: Schema-based validation

## 🎓 Learning Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **JSON Schema**: https://json-schema.org/
- **Dynamic Forms**: Study the `FormBuilder` class
- **Multi-Tenancy**: Organization-based separation pattern

---

## 🆘 Troubleshooting

### Migration Issues
See `MIGRATION_FIX_GUIDE.md` for detailed solutions.

### Common Problems
1. **Missing Dependencies**: Install all requirements
2. **Database Locked**: Stop server before migrations
3. **Permission Errors**: Use proper file permissions
4. **Schema Loading**: Check SCHEMA_ROOT setting

### Getting Help
1. Check the migration guide
2. Review sample configurations
3. Test with provided demo data
4. Use the admin interface for debugging

---

**Built with Django 5.2+ | Python 3.8+ | Bootstrap 5**

This system demonstrates enterprise-level configurability while maintaining Django's simplicity and power. Perfect for organizations needing flexible, scalable form management without constant code changes.