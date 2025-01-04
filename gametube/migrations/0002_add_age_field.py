
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('gametube', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='age',
            field=models.IntegerField(null=True),
        ),
    ]
