
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('gametube', '0003_merge_0002_add_age_field_0002_auto_20241226_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='age_restriction',
            field=models.CharField(choices=[('all', '制限なし'), ('r15', '15歳以上'), ('r18', '18歳以上')], default='all', max_length=5),
        ),
    ]
