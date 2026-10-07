from django.contrib import admin

from .models import TimetableSlot


@admin.register(TimetableSlot)
class TimetableSlotAdmin(admin.ModelAdmin):
    list_display = ('department', 'semester', 'division', 'batch', 'weekday', 'batch_end_time', 'start_time', 'end_time')
    list_filter = ('department', 'semester', 'division', 'batch', 'weekday')

    fields = ('department', 'semester', 'division', 'batch', 'weekday', 'batch_end_time', 'start_time', 'end_time')

    class Media:
        js = ('timetable/prefill_attendance_window.js',)
