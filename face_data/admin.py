from django.contrib import admin

from .models import FaceData


@admin.register(FaceData)
class FaceDataAdmin(admin.ModelAdmin):
    list_display = ('student', 'model_name', 'created_at')
    search_fields = ('student__student_id', 'student__full_name')
    readonly_fields = ('created_at', 'updated_at')
