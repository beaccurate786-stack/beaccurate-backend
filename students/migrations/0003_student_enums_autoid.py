from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_alter_student_profile_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='student_id',
            field=models.CharField(editable=False, max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='department',
            field=models.CharField(choices=[('computer', 'Computer'), ('ec', 'EC')], max_length=20),
        ),
        migrations.AlterField(
            model_name='student',
            name='semester',
            field=models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6')]),
        ),
        migrations.AlterField(
            model_name='student',
            name='division',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B')], max_length=1),
        ),
    ]
