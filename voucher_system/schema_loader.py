import os
import yaml
import json
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class SchemaLoader:
    """Loads and merges voucher schemas from YAML files and database config"""
    
    def __init__(self):
        self.schema_root = getattr(settings, 'SCHEMA_ROOT', None)
        if not self.schema_root:
            # Fallback to app directory if SCHEMA_ROOT not set
            from django.apps import apps
            app_config = apps.get_app_config('voucher_system')
            self.schema_root = os.path.join(app_config.path, 'schemas')
    
    def load_default_schema(self):
        """Load the default schema template"""
        return {
            "header": {
                "date": {
                    "type": "date",
                    "label": "Date",
                    "required": True,
                    "widget": "date"
                },
                "journal_type": {
                    "type": "select",
                    "label": "Journal Type",
                    "required": True,
                    "choices": "JournalType"
                },
                "voucher_number": {
                    "type": "text",
                    "label": "Voucher Number",
                    "required": True,
                    "max_length": 50
                },
                "reference_number": {
                    "type": "text",
                    "label": "Reference Number",
                    "required": False,
                    "max_length": 100
                },
                "narration": {
                    "type": "textarea",
                    "label": "Narration",
                    "required": False,
                    "rows": 3
                }
            },
            "lines": {
                "account_code": {
                    "type": "text",
                    "label": "Account Code",
                    "required": True,
                    "max_length": 50
                },
                "account_name": {
                    "type": "text",
                    "label": "Account Name",
                    "required": True,
                    "max_length": 200
                },
                "narration": {
                    "type": "text",
                    "label": "Narration",
                    "required": False
                },
                "debit_amount": {
                    "type": "decimal",
                    "label": "Debit Amount",
                    "required": False,
                    "min_value": 0,
                    "decimal_places": 2
                },
                "credit_amount": {
                    "type": "decimal",
                    "label": "Credit Amount",
                    "required": False,
                    "min_value": 0,
                    "decimal_places": 2
                }
            }
        }
    
    def load_schema_file(self, filename):
        """Load schema from YAML file"""
        if not os.path.exists(self.schema_root):
            return {}
            
        file_path = os.path.join(self.schema_root, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading schema file {filename}: {e}")
        return {}
    
    def merge_schemas(self, base_schema, override_schema):
        """Deep merge two schema dictionaries"""
        if not override_schema:
            return base_schema
        
        merged = base_schema.copy()
        
        for section in ['header', 'lines']:
            if section in override_schema:
                if section not in merged:
                    merged[section] = {}
                merged[section].update(override_schema[section])
        
        return merged
    
    def add_udf_fields(self, schema, voucher_config):
        """Add UDF fields to schema"""
        try:
            from .models import VoucherUDFConfig
            
            udf_configs = VoucherUDFConfig.objects.filter(
                voucher_config=voucher_config,
                is_active=True
            ).order_by('display_order')
            
            for udf in udf_configs:
                field_def = {
                    "type": udf.field_type,
                    "label": udf.display_name,
                    "required": udf.is_required,
                    "help_text": udf.help_text,
                    "default": udf.default_value
                }
                
                # Add validation constraints
                if udf.min_value is not None:
                    field_def["min_value"] = float(udf.min_value)
                if udf.max_value is not None:
                    field_def["max_value"] = float(udf.max_value)
                if udf.min_length:
                    field_def["min_length"] = udf.min_length
                if udf.max_length:
                    field_def["max_length"] = udf.max_length
                if udf.validation_regex:
                    field_def["pattern"] = udf.validation_regex
                
                # Add choices for select fields
                if udf.field_type in ['select', 'multiselect'] and udf.choices_config:
                    field_def["choices"] = udf.choices_config
                
                # Add conditional logic
                if udf.condition_json:
                    field_def["condition"] = udf.condition_json
                
                # Add to appropriate section
                section = udf.scope
                if section not in schema:
                    schema[section] = {}
                
                field_name = f"udf_{udf.field_name}"
                schema[section][field_name] = field_def
        
        except Exception as e:
            print(f"Error adding UDF fields: {e}")
        
        return schema
    
    def get_merged_schema(self, voucher_config):
        """Get the final merged schema for a voucher configuration"""
        # Start with default schema
        schema = self.load_default_schema()
        
        # Try to load specific schema file
        schema_files = [
            f"{voucher_config.code}.yml",
            f"{voucher_config.code}.yaml",
            "general.yml",
            "standard.yml"
        ]
        
        for filename in schema_files:
            file_schema = self.load_schema_file(filename)
            if file_schema:
                schema = self.merge_schemas(schema, file_schema)
                break
        
        # Merge with database configuration
        if voucher_config.ui_schema:
            schema = self.merge_schemas(schema, voucher_config.ui_schema)
        
        # Add UDF fields
        schema = self.add_udf_fields(schema, voucher_config)
        
        return schema