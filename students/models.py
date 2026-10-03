from django.db import models


class Student(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    student_id = models.CharField(max_length=30, unique=True)
    roll_number = models.CharField(max_length=30, db_index=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100)
    semester = models.PositiveSmallIntegerField()
    division = models.CharField(max_length=30)
    profile_photo = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('student_id',)
        indexes = [
            models.Index(fields=('department', 'semester', 'division')),
            models.Index(fields=('status',)),
        ]

    def __str__(self):
        return f'{self.student_id} — {self.full_name}'
