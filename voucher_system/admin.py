from django.contrib import admin
from .models import (
    Organization, JournalType, VoucherModeConfig, 
    VoucherUDFConfig, VoucherModeDefault, Journal, JournalLine
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at']


@admin.register(JournalType)
class JournalTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description']
    search_fields = ['name', 'code']


@admin.register(VoucherModeConfig)
class VoucherModeConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'organization', 'layout_style', 'is_active']
    list_filter = ['organization', 'layout_style', 'is_active']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'name', 'code', 'description', 'is_active')
        }),
        ('Configuration', {
            'fields': ('layout_style', 'ui_schema', 'validation_rules', 'default_narration_template')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VoucherUDFConfig)
class VoucherUDFConfigAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'field_name', 'voucher_config', 'field_type', 'scope', 'is_active']
    list_filter = ['field_type', 'scope', 'is_active', 'voucher_config']
    search_fields = ['display_name', 'field_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('voucher_config', 'organization', 'field_name', 'display_name', 'field_type', 'scope')
        }),
        ('Properties', {
            'fields': ('is_required', 'default_value', 'help_text', 'display_order', 'is_active')
        }),
        ('Validation', {
            'fields': ('min_value', 'max_value', 'min_length', 'max_length', 'validation_regex'),
            'classes': ('collapse',)
        }),
        ('Advanced', {
            'fields': ('choices_config', 'condition_json'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VoucherModeDefault)
class VoucherModeDefaultAdmin(admin.ModelAdmin):
    list_display = ['voucher_config', 'account_name', 'account_code', 'default_amount', 'display_order']
    list_filter = ['voucher_config']
    search_fields = ['account_name', 'account_code']


class JournalLineInline(admin.TabularInline):
    model = JournalLine
    extra = 1
    fields = ['account_code', 'account_name', 'narration', 'debit_amount', 'credit_amount']


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ['voucher_number', 'date', 'journal_type', 'organization', 'is_posted', 'total_debit', 'total_credit']
    list_filter = ['journal_type', 'organization', 'is_posted', 'date']
    search_fields = ['voucher_number', 'reference_number']
    inlines = [JournalLineInline]
    readonly_fields = ['created_at', 'updated_at', 'total_debit', 'total_credit']
    
    fieldsets = (
        ('Voucher Information', {
            'fields': ('organization', 'voucher_config', 'voucher_number', 'date', 'journal_type')
        }),
        ('Details', {
            'fields': ('reference_number', 'narration', 'udf_values')
        }),
        ('Status', {
            'fields': ('is_posted',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'total_debit', 'total_credit'),
            'classes': ('collapse',)
        }),
    )
    
    def total_debit(self, obj):
        return f"₹ {obj.total_debit:,.2f}"
    total_debit.short_description = 'Total Debit'
    
    def total_credit(self, obj):
        return f"₹ {obj.total_credit:,.2f}"
    total_credit.short_description = 'Total Credit'