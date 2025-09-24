# Generated migration to make organization fields required

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voucher_system', '0002_add_default_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voucher_system.organization'),
        ),
        migrations.AlterField(
            model_name='vouchermodeconfig',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voucher_system.organization'),
        ),
        migrations.AlterField(
            model_name='voucherudfconfig',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voucher_system.organization'),
        ),
    ]