from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faculty',
            name='faculty_id',
            field=models.CharField(editable=False, max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='faculty',
            name='department',
            field=models.CharField(choices=[('computer', 'Computer'), ('ec', 'EC')], max_length=20),
        ),
    ]
