from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date

from students.access import can_access_panel, filter_students_for
from students.enums import Role
from students.models import Student

from .models import Attendance


def can_manage_attendance(user):
    """Only HODs, mentors, and superadmins may access or correct the log."""
    if not can_access_panel(user):
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=(Role.SUPER_ADMIN, Role.HOD, Role.MENTOR)).exists()


@user_passes_test(can_manage_attendance, login_url='admin:login')
def home(request):
    """Show the attendance log and let authorized staff correct attendance status."""
    students = filter_students_for(request.user, Student.objects.all())
    records = Attendance.objects.select_related('student').filter(student__in=students)
    editable_statuses = (
        (Attendance.Status.PRESENT, 'Present'),
        (Attendance.Status.ABSENT, 'Absent'),
    )

    if request.method == 'POST':
        record = get_object_or_404(records, pk=request.POST.get('record_id'))
        new_status = request.POST.get('status')
        editable_status_values = (
            Attendance.Status.PRESENT,
            Attendance.Status.ABSENT,
        )
        if new_status not in editable_status_values:
            messages.error(request, 'Choose Present or Absent.')
        else:
            record.status = new_status
            record.recognition_method = Attendance.RecognitionMethod.MANUAL
            record.recognition_confidence = None
            if record.time is None:
                record.time = timezone.localtime().time().replace(microsecond=0)
            record.save(update_fields=(
                'status', 'recognition_method', 'recognition_confidence', 'time', 'updated_at',
            ))
            messages.success(request, f'Attendance updated for {record.student.full_name} on {record.date:%b %d, %Y}.')

        query = request.GET.urlencode()
        return redirect(f'{reverse("attendance:log")}?{query}' if query else 'attendance:log')

    start_date_value = request.GET.get('start_date', '').strip()
    end_date_value = request.GET.get('end_date', '').strip()
    start_date = parse_date(start_date_value) if start_date_value else None
    end_date = parse_date(end_date_value) if end_date_value else None
    search = request.GET.get('q', '').strip()

    if start_date:
        records = records.filter(date__gte=start_date)
    if end_date:
        records = records.filter(date__lte=end_date)
    if search:
        records = records.filter(
            Q(student__full_name__icontains=search)
            | Q(student__student_id__icontains=search)
            | Q(student__roll_number__icontains=search)
        )

    return render(request, 'attendance/home.html', {
        'records': records,
        'start_date': start_date_value,
        'end_date': end_date_value,
        'search': search,
        'editable_statuses': editable_statuses,
    })
