from django.contrib import admin

from .models import Faculty


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'full_name', 'email', 'department', 'designation', 'status')
    list_filter = ('status', 'department', 'designation')
    search_fields = ('faculty_id', 'full_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
