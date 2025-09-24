from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import json
import yaml


class Organization(models.Model):
    """Organization model for multi-tenancy"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name


class JournalType(models.Model):
    """Journal types for voucher categorization"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class VoucherModeConfig(models.Model):
    """Core model for voucher configuration"""
    LAYOUT_CHOICES = [
        ('standard', 'Standard'),
        ('compact', 'Compact'),
        ('detailed', 'Detailed'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    # UI Schema (JSON field for form definition)
    ui_schema = models.JSONField(default=dict, blank=True)
    
    # Layout and styling
    layout_style = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='standard')
    
    # Validation rules (JSON field for complex validation)
    validation_rules = models.JSONField(default=dict, blank=True)
    
    # Default values and templates
    default_narration_template = models.TextField(blank=True)
    
    # Status and metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ['organization', 'code']
    
    def __str__(self):
        org_name = self.organization.code if self.organization else 'No Org'
        return f"{org_name} - {self.name}"
    
    def get_merged_schema(self):
        """Merge voucher-specific schema with default schema"""
        from .schema_loader import SchemaLoader
        loader = SchemaLoader()
        return loader.get_merged_schema(self)


class VoucherUDFConfig(models.Model):
    """User-Defined Fields configuration"""
    FIELD_TYPES = [
        ('text', 'Text'),
        ('textarea', 'Text Area'),
        ('number', 'Number'),
        ('decimal', 'Decimal'),
        ('date', 'Date'),
        ('datetime', 'Date Time'),
        ('select', 'Select'),
        ('multiselect', 'Multi Select'),
        ('checkbox', 'Checkbox'),
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('url', 'URL'),
    ]
    
    SCOPE_CHOICES = [
        ('header', 'Header'),
        ('line', 'Line'),
    ]
    
    voucher_config = models.ForeignKey(VoucherModeConfig, on_delete=models.CASCADE, related_name='udf_configs')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    
    # Field definition
    field_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES)
    
    # Field properties
    is_required = models.BooleanField(default=False)
    default_value = models.TextField(blank=True)
    help_text = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)
    
    # Validation constraints
    min_value = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    max_value = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    min_length = models.IntegerField(null=True, blank=True)
    max_length = models.IntegerField(null=True, blank=True)
    validation_regex = models.CharField(max_length=500, blank=True)
    
    # Choices for select fields (JSON)
    choices_config = models.JSONField(default=dict, blank=True)
    
    # Conditional logic (JSON)
    condition_json = models.JSONField(default=dict, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['voucher_config', 'field_name', 'scope']
    
    def __str__(self):
        return f"{self.voucher_config.name} - {self.display_name}"


class VoucherModeDefault(models.Model):
    """Default line items for voucher types"""
    voucher_config = models.ForeignKey(VoucherModeConfig, on_delete=models.CASCADE, related_name='defaults')
    account_code = models.CharField(max_length=50)
    account_name = models.CharField(max_length=200)
    default_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    narration = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.voucher_config.name} - {self.account_name}"


class Journal(models.Model):
    """Main voucher/journal entry model"""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    voucher_config = models.ForeignKey(VoucherModeConfig, on_delete=models.CASCADE)
    
    # Standard fields
    voucher_number = models.CharField(max_length=50)
    date = models.DateField()
    journal_type = models.ForeignKey(JournalType, on_delete=models.CASCADE)
    reference_number = models.CharField(max_length=100, blank=True)
    narration = models.TextField(blank=True)
    
    # UDF values (JSON field to store user-defined field values)
    udf_values = models.JSONField(default=dict, blank=True)
    
    # Status and metadata
    is_posted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.voucher_number} - {self.date}"
    
    @property
    def total_debit(self):
        return sum(line.debit_amount for line in self.lines.all())
    
    @property
    def total_credit(self):
        return sum(line.credit_amount for line in self.lines.all())


class JournalLine(models.Model):
    """Journal line items"""
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='lines')
    
    # Line fields
    account_code = models.CharField(max_length=50)
    account_name = models.CharField(max_length=200)
    narration = models.TextField(blank=True)
    debit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    
    # UDF values for line-level custom fields
    udf_values = models.JSONField(default=dict, blank=True)
    
    # Line order
    line_number = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.journal.voucher_number} - Line {self.line_number}"