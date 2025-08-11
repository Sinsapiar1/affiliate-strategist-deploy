# analyzer/migrations/0002_add_reset_date.py

from django.db import migrations, models
from django.utils import timezone

class Migration(migrations.Migration):
    
    dependencies = [
        ('analyzer', '0001_initial'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='last_reset_date',
            field=models.DateTimeField(default=timezone.now),
        ),
    ]