from django.db import models, transaction

from .enums import Batch, Department, Division, Semester, StudentStatus


class Student(models.Model):
    Status = StudentStatus
    STUDENT_ID_PREFIX = 'STU'

    student_id = models.CharField(max_length=30, unique=True, editable=False)
    roll_number = models.CharField(max_length=30, db_index=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=20, choices=Department.choices)
    semester = models.PositiveSmallIntegerField(choices=Semester.choices)
    division = models.CharField(max_length=1, choices=Division.choices)
    batch = models.CharField(max_length=1, choices=Batch.choices, default='')
    profile_photo = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('student_id',)
        indexes = [
            models.Index(fields=('department', 'semester', 'division', 'batch')),
            models.Index(fields=('status',)),
        ]

    def save(self, *args, **kwargs):
        if not self.student_id:
            with transaction.atomic():
                self.student_id = self._next_student_id()
                return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    @classmethod
    def _next_student_id(cls):
        prefix = cls.STUDENT_ID_PREFIX
        last = (
            cls.objects.select_for_update()
            .filter(student_id__startswith=prefix)
            .order_by('-student_id')
            .values_list('student_id', flat=True)
            .first()
        )
        number = int(last[len(prefix):]) + 1 if last else 1
        return f'{prefix}{number:05d}'

    def __str__(self):
        return f'{self.student_id} — {self.full_name}'


