# Generated migration to add default organization

from django.db import migrations


def create_default_organization(apps, schema_editor):
    Organization = apps.get_model('voucher_system', 'Organization')
    VoucherModeConfig = apps.get_model('voucher_system', 'VoucherModeConfig')
    VoucherUDFConfig = apps.get_model('voucher_system', 'VoucherUDFConfig')
    Journal = apps.get_model('voucher_system', 'Journal')
    
    # Create default organization if it doesn't exist
    default_org, created = Organization.objects.get_or_create(
        code='DEFAULT',
        defaults={'name': 'Default Organization'}
    )
    
    # Update all existing records to use the default organization
    VoucherModeConfig.objects.filter(organization__isnull=True).update(organization=default_org)
    VoucherUDFConfig.objects.filter(organization__isnull=True).update(organization=default_org)
    Journal.objects.filter(organization__isnull=True).update(organization=default_org)


def reverse_create_default_organization(apps, schema_editor):
    # This migration is not easily reversible
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('voucher_system', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_default_organization,
            reverse_create_default_organization,
        ),
    ]