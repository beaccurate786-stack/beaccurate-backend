import datetime

from django.core.exceptions import ValidationError
from django.db import models

from students.enums import Batch, Department, Division, Semester, Weekday


ATTENDANCE_MARGIN = datetime.timedelta(minutes=10)


def shift_time(value, delta):
    """``value`` moved by ``delta``, kept within the same day."""
    moved = datetime.datetime.combine(datetime.date.min, value) + delta
    day_start = datetime.datetime.combine(datetime.date.min, datetime.time.min)
    day_end = datetime.datetime.combine(datetime.date.min, datetime.time(23, 59))
    return min(max(moved, day_start), day_end).time()


class TimetableSlot(models.Model):
    """When a batch has its session on a weekday. Attendance can only be marked inside it."""

    department = models.CharField(max_length=20, choices=Department.choices)
    semester = models.PositiveSmallIntegerField(choices=Semester.choices)
    division = models.CharField(max_length=1, choices=Division.choices)
    batch = models.CharField(max_length=1, choices=Batch.choices)
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    batch_end_time = models.TimeField(
        null=True,
        help_text='When the batch session ends. The attendance window below is prefilled around it.',
    )
    start_time = models.TimeField(
        blank=True,
        verbose_name='Attendance start time',
        help_text='Prefilled as 10 minutes before the batch end time.',
    )
    end_time = models.TimeField(
        blank=True,
        verbose_name='Attendance end time',
        help_text='Prefilled as 10 minutes after the batch end time.',
    )

    class Meta:
        ordering = ('department', 'semester', 'division', 'batch', 'weekday', 'start_time')
        constraints = [
            models.UniqueConstraint(
                fields=('department', 'semester', 'division', 'batch', 'weekday', 'start_time'),
                name='unique_timetable_slot',
            ),
        ]
        indexes = [models.Index(fields=('department', 'semester', 'division', 'batch', 'weekday'))]

    def fill_attendance_window(self):
        """Default the attendance window to batch end time -10 / +10 minutes."""
        if self.batch_end_time:
            if not self.start_time:
                self.start_time = shift_time(self.batch_end_time, -ATTENDANCE_MARGIN)
            if not self.end_time:
                self.end_time = shift_time(self.batch_end_time, ATTENDANCE_MARGIN)

    def save(self, *args, **kwargs):
        self.fill_attendance_window()
        super().save(*args, **kwargs)

    def clean(self):
        self.fill_attendance_window()
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError({'end_time': 'End time must be after the start time.'})
        if self.start_time and self.end_time and self.weekday is not None:
            overlapping = TimetableSlot.objects.filter(
                department=self.department, semester=self.semester, division=self.division,
                batch=self.batch, weekday=self.weekday,
                start_time__lt=self.end_time, end_time__gt=self.start_time,
            ).exclude(pk=self.pk)
            if overlapping.exists():
                raise ValidationError('This overlaps another slot of the same batch on that day.')

    def __str__(self):
        return (f'{self.get_department_display()} Sem {self.semester} {self.division}/{self.batch} — '
                f'{self.get_weekday_display()} {self.start_time:%H:%M}-{self.end_time:%H:%M}')
