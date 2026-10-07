from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from students.admin_import import CsvImportAdminMixin

from .models import Faculty


@admin.register(Faculty)
class FacultyAdmin(CsvImportAdminMixin, admin.ModelAdmin):
    import_columns = ('full_name', 'email', 'phone_number', 'department', 'semester', 'division', 'status')
    import_required = ('full_name', 'email', 'department', 'semester', 'division')
    import_excluded_validation = ('faculty_id', 'user')
    list_display = ('faculty_id', 'full_name', 'email', 'department', 'semester', 'division', 'student_count', 'status')
    list_filter = ('status', 'department', 'semester', 'division')
    search_fields = ('faculty_id', 'full_name', 'email')
    readonly_fields = ('created_at', 'updated_at', 'student_list')

    @admin.display(description='Students')
    def student_count(self, obj):
        return obj.related_students().count()

    @admin.display(description='Related students')
    def student_list(self, obj):
        if not obj.pk:
            return 'Save the faculty to see the students of the selected semester and division.'
        students = obj.related_students()
        if not students:
            return 'No students in this semester and division.'
        return format_html_join(
            format_html('<br>'),
            '<a href="{}">{} — {}</a>',
            (
                (reverse('admin:students_student_change', args=(s.pk,)), s.student_id, s.full_name)
                for s in students
            ),
        )
