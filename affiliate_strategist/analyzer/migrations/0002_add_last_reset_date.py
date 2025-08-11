# Generated migration for last_reset_date field

from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='last_reset_date',
            field=models.DateField(default=django.utils.timezone.now, help_text='Fecha del último reset del contador mensual'),
        ),
    ]
