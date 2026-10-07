from django.conf import settings
from django.db import models, transaction

from students.enums import Department, Division, Role, Semester


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
    semester = models.PositiveSmallIntegerField(choices=Semester.choices, null=True)
    division = models.CharField(max_length=1, choices=Division.choices, default='')
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faculty_profile',
        limit_choices_to={'groups__name': Role.MENTOR},
        help_text='Login account (Mentor group). Lets this faculty sign in and see their students.',
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('faculty_id',)
        indexes = [models.Index(fields=('department', 'status'))]

    def related_students(self):
        """Students in this faculty's semester and division."""
        from students.models import Student

        if self.semester is None or not self.division:
            return Student.objects.none()
        return Student.objects.filter(semester=self.semester, division=self.division)

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
