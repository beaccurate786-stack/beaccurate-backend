from django.contrib import admin

from .models import AttendanceModification


@admin.register(AttendanceModification)
class AttendanceModificationAdmin(admin.ModelAdmin):
    list_display = ('attendance', 'faculty', 'previous_status', 'new_status', 'reason', 'modified_at')
    list_filter = ('previous_status', 'new_status', 'modified_at')
    search_fields = ('attendance__student__student_id', 'faculty__faculty_id', 'reason')
    readonly_fields = ('modified_at',)

# Register your models here.
