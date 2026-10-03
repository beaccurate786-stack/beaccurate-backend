from django.db import models


class FaceData(models.Model):
    student = models.OneToOneField('students.Student', on_delete=models.CASCADE, related_name='face_data')
    face_embedding = models.JSONField(help_text='Future SFace numeric embedding; no recognition logic is implemented here.')
    model_name = models.CharField(max_length=100, default='SFace')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Face data for {self.student}'
