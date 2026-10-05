from django.contrib import admin

from .admin_import import CsvImportAdminMixin
from .models import Student


@admin.register(Student)
class StudentAdmin(CsvImportAdminMixin, admin.ModelAdmin):
    import_columns = ('roll_number', 'full_name', 'email', 'phone_number', 'department', 'semester', 'division', 'status')
    import_required = ('roll_number', 'full_name', 'email', 'department', 'semester', 'division')
    import_excluded_validation = ('student_id',)
    list_display = ('student_id', 'roll_number', 'full_name', 'department', 'semester', 'division', 'status')
    list_filter = ('status', 'department', 'semester', 'division')
    search_fields = ('student_id', 'roll_number', 'full_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
