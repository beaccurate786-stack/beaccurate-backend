import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('students', '0003_student_enums_autoid'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MentorAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6')])),
                ('division', models.CharField(choices=[('A', 'A'), ('B', 'B')], max_length=1)),
                ('user', models.ForeignKey(limit_choices_to={'groups__name': 'Mentor'}, on_delete=django.db.models.deletion.CASCADE, related_name='mentor_assignments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user', 'semester', 'division'),
                'constraints': [models.UniqueConstraint(fields=('user', 'semester', 'division'), name='unique_mentor_semester_division')],
            },
        ),
    ]
