from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import TimetableSlot


def open_slot_for(student, when=None):
    """The slot of the student's batch that is running at ``when`` (default: now), or None."""
    when = timezone.localtime(when) if when else timezone.localtime()
    return TimetableSlot.objects.filter(
        department=student.department,
        semester=student.semester,
        division=student.division,
        batch=student.batch,
        weekday=when.weekday(),
        start_time__lte=when.time(),
        end_time__gte=when.time(),
    ).first()


def ensure_attendance_open(student, when=None):
    """Raise ValidationError unless the student's batch has a session running at ``when``."""
    if open_slot_for(student, when) is None:
        raise ValidationError(
            f'Attendance for {student.student_id} can only be marked during the timetable slot of their batch.'
        )
