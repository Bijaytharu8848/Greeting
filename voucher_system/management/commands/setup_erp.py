from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from voucher_system.models import *


class Command(BaseCommand):
    help = 'Setup ERP system with sample data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all data before creating sample data',
        )
    
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting data...')
            Journal.objects.all().delete()
            VoucherUDFConfig.objects.all().delete()
            VoucherModeConfig.objects.all().delete()
            JournalType.objects.all().delete()
            Organization.objects.all().delete()
        
        self.stdout.write('Setting up ERP system...')
        
        # Create default organization
        org, created = Organization.objects.get_or_create(
            code='DEMO',
            defaults={'name': 'Demo Organization'}
        )
        self.stdout.write(f'Organization: {org} ({"created" if created else "exists"})')
        
        # Create journal types
        journal_types = [
            ('CASH', 'Cash Receipt'),
            ('BANK', 'Bank Payment'),
            ('JOURNAL', 'General Journal'),
            ('PURCHASE', 'Purchase Entry'),
            ('SALES', 'Sales Entry'),
        ]
        
        for code, name in journal_types:
            jt, created = JournalType.objects.get_or_create(
                code=code,
                defaults={'name': name}
            )
            self.stdout.write(f'Journal Type: {jt} ({"created" if created else "exists"})')
        
        # Get or create admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        
        # Create voucher configurations
        configs = [
            {
                'code': 'CASH_RECEIPT',
                'name': 'Cash Receipt Voucher',
                'description': 'Configuration for cash receipt entries',
                'ui_schema': {
                    'header': {
                        'received_from': {
                            'type': 'text',
                            'label': 'Received From',
                            'required': True,
                            'max_length': 200
                        }
                    }
                }
            },
            {
                'code': 'PAYMENT',
                'name': 'Payment Voucher',
                'description': 'Configuration for payment entries',
                'ui_schema': {
                    'header': {
                        'pay_to': {
                            'type': 'text',
                            'label': 'Pay To',
                            'required': True,
                            'max_length': 200
                        }
                    }
                }
            },
            {
                'code': 'JOURNAL',
                'name': 'General Journal',
                'description': 'General journal entry configuration',
                'ui_schema': {}
            }
        ]
        
        for config_data in configs:
            config, created = VoucherModeConfig.objects.get_or_create(
                organization=org,
                code=config_data['code'],
                defaults={
                    'name': config_data['name'],
                    'description': config_data['description'],
                    'ui_schema': config_data['ui_schema'],
                    'created_by': admin_user
                }
            )
            self.stdout.write(f'Voucher Config: {config} ({"created" if created else "exists"})')
            
            # Add sample UDF for cash receipt
            if config_data['code'] == 'CASH_RECEIPT':
                udf, created = VoucherUDFConfig.objects.get_or_create(
                    voucher_config=config,
                    organization=org,
                    field_name='receipt_mode',
                    defaults={
                        'display_name': 'Receipt Mode',
                        'field_type': 'select',
                        'scope': 'header',
                        'is_required': True,
                        'choices_config': {
                            'cash': 'Cash',
                            'cheque': 'Cheque',
                            'online': 'Online Transfer'
                        },
                        'display_order': 1
                    }
                )
                self.stdout.write(f'UDF: {udf} ({"created" if created else "exists"})')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up ERP system with sample data!')
        )
        
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Create superuser: python3 manage.py createsuperuser')
        self.stdout.write('2. Run server: python3 manage.py runserver')
        self.stdout.write('3. Access admin: http://127.0.0.1:8000/admin/')