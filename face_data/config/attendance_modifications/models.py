from django.db import models


class AttendanceModification(models.Model):
    attendance = models.ForeignKey('attendance.Attendance', on_delete=models.CASCADE, related_name='modifications')
    faculty = models.ForeignKey('faculty.Faculty', on_delete=models.PROTECT, related_name='attendance_modifications')
    previous_status = models.CharField(max_length=15, choices=[
        ('present', 'Present'), ('absent', 'Absent'), ('late', 'Late'), ('not_marked', 'Not Marked'),
    ])
    new_status = models.CharField(max_length=15, choices=[
        ('present', 'Present'), ('absent', 'Absent'), ('late', 'Late'), ('not_marked', 'Not Marked'),
    ])
    reason = models.TextField()
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-modified_at',)

    def __str__(self):
        return f'{self.attendance} modified by {self.faculty}'

# Create your models here.
