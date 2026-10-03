from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'roll_number', 'full_name', 'department', 'semester', 'division', 'status')
    list_filter = ('status', 'department', 'semester', 'division')
    search_fields = ('student_id', 'roll_number', 'full_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
