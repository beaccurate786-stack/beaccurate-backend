from django.db import models, transaction

from students.enums import Department


class Faculty(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    FACULTY_ID_PREFIX = 'FAC'

    faculty_id = models.CharField(max_length=30, unique=True, editable=False)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=20, choices=Department.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('faculty_id',)
        indexes = [models.Index(fields=('department', 'status'))]

    def save(self, *args, **kwargs):
        if not self.faculty_id:
            with transaction.atomic():
                self.faculty_id = self._next_faculty_id()
                return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    @classmethod
    def _next_faculty_id(cls):
        prefix = cls.FACULTY_ID_PREFIX
        last = (
            cls.objects.select_for_update()
            .filter(faculty_id__startswith=prefix)
            .order_by('-faculty_id')
            .values_list('faculty_id', flat=True)
            .first()
        )
        number = int(last[len(prefix):]) + 1 if last else 1
        return f'{prefix}{number:05d}'

    def __str__(self):
        return f'{self.faculty_id} — {self.full_name}'
