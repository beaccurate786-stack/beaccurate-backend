import datetime

from django.db import models
from django.utils import timezone


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        LATE = 'late', 'Late'
        NOT_MARKED = 'not_marked', 'Not Marked'

    class RecognitionMethod(models.TextChoices):
        FACE_RECOGNITION = 'face_recognition', 'Face Recognition'
        MANUAL = 'manual', 'Manual'

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.NOT_MARKED)
    recognition_method = models.CharField(max_length=20, choices=RecognitionMethod.choices, default=RecognitionMethod.MANUAL)
    recognition_confidence = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-date', 'student__student_id')
        constraints = [
            models.UniqueConstraint(fields=('student', 'date'), name='unique_student_attendance_per_day'),
        ]
        indexes = [models.Index(fields=('date', 'status'))]

    def clean(self):
        # Attendance may only be marked while the student's batch has a timetable slot running.
        if self.status != self.Status.NOT_MARKED and self.student_id and self.date:
            from timetable.services import ensure_attendance_open

            when = timezone.make_aware(datetime.datetime.combine(self.date, self.time or timezone.localtime().time()))
            ensure_attendance_open(self.student, when)

    def __str__(self):
        return f'{self.student} - {self.date} ({self.get_status_display()})'


class AttendanceModification(models.Model):
    """Legacy audit table retained to preserve any existing records."""

    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='legacy_modifications')
    faculty = models.ForeignKey('faculty.Faculty', on_delete=models.PROTECT, related_name='legacy_attendance_modifications')
    previous_status = models.CharField(max_length=15, choices=Attendance.Status.choices)
    new_status = models.CharField(max_length=15, choices=Attendance.Status.choices)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.attendance} modified by {self.faculty}'
