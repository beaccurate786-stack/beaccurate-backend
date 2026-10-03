from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'time', 'status', 'recognition_method', 'recognition_confidence')
    list_filter = ('status', 'recognition_method', 'date')
    search_fields = ('student__student_id', 'student__full_name')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
