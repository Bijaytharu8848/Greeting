from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import (
    VoucherModeConfig, Journal, JournalLine, 
    Organization, JournalType, VoucherUDFConfig
)
from .schema_loader import SchemaLoader


def home(request):
    """Home page showing available voucher configurations"""
    configs = VoucherModeConfig.objects.filter(is_active=True).select_related('organization')
    return render(request, 'voucher_system/home.html', {'configs': configs})


def voucher_config_detail(request, config_id):
    """Show voucher configuration details and schema"""
    config = get_object_or_404(VoucherModeConfig, id=config_id, is_active=True)
    
    # Load the merged schema
    loader = SchemaLoader()
    schema = loader.get_merged_schema(config)
    
    # Get UDF configurations
    udfs = VoucherUDFConfig.objects.filter(
        voucher_config=config, 
        is_active=True
    ).order_by('display_order')
    
    context = {
        'config': config,
        'schema': schema,
        'udfs': udfs,
        'schema_json': json.dumps(schema, indent=2)
    }
    
    return render(request, 'voucher_system/config_detail.html', context)


def schema_preview(request, config_id):
    """API endpoint to preview schema as JSON"""
    config = get_object_or_404(VoucherModeConfig, id=config_id, is_active=True)
    
    loader = SchemaLoader()
    schema = loader.get_merged_schema(config)
    
    return JsonResponse({
        'config': {
            'id': config.id,
            'name': config.name,
            'code': config.code,
            'organization': config.organization.name
        },
        'schema': schema
    }, indent=2)


def test_dynamic_form(request, config_id):
    """Test page to show how dynamic forms would be generated"""
    config = get_object_or_404(VoucherModeConfig, id=config_id, is_active=True)
    
    loader = SchemaLoader()
    schema = loader.get_merged_schema(config)
    
    # Simulate form field generation
    header_fields = []
    for field_name, field_config in schema.get('header', {}).items():
        header_fields.append({
            'name': field_name,
            'label': field_config.get('label', field_name),
            'type': field_config.get('type', 'text'),
            'required': field_config.get('required', False),
            'help_text': field_config.get('help_text', ''),
            'choices': field_config.get('choices', [])
        })
    
    line_fields = []
    for field_name, field_config in schema.get('lines', {}).items():
        line_fields.append({
            'name': field_name,
            'label': field_config.get('label', field_name),
            'type': field_config.get('type', 'text'),
            'required': field_config.get('required', False),
            'help_text': field_config.get('help_text', ''),
            'choices': field_config.get('choices', [])
        })
    
    context = {
        'config': config,
        'header_fields': header_fields,
        'line_fields': line_fields,
        'journal_types': JournalType.objects.all()
    }
    
    return render(request, 'voucher_system/test_form.html', context)