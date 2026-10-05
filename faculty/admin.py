from django.contrib import admin

from students.admin_import import CsvImportAdminMixin

from .models import Faculty


@admin.register(Faculty)
class FacultyAdmin(CsvImportAdminMixin, admin.ModelAdmin):
    import_columns = ('full_name', 'email', 'phone_number', 'department', 'status')
    import_required = ('full_name', 'email', 'department')
    import_excluded_validation = ('faculty_id',)
    list_display = ('faculty_id', 'full_name', 'email', 'department', 'status')
    list_filter = ('status', 'department')
    search_fields = ('faculty_id', 'full_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
