import io
import tempfile
from datetime import date, time

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from attendance_modifications.models import AttendanceModification
from face_data.models import FaceData
from faculty.models import Faculty
from students.models import Student

from .models import Attendance


class HomeViewTests(TestCase):
    def test_home_page_is_available(self):
        response = self.client.get(reverse('attendance:home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Attendance System')


class AttendanceDataModelTests(TestCase):
    def test_related_records_and_profile_photo_can_be_saved(self):
        image_buffer = io.BytesIO()
        Image.new('RGB', (1, 1), color='white').save(image_buffer, format='PNG')
        photo = SimpleUploadedFile('student.png', image_buffer.getvalue(), content_type='image/png')

        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            student = Student.objects.create(
                student_id='TEST-STUDENT', roll_number='TEST-001', full_name='System Test Student',
                email='system.test.student@example.com', department='Testing', semester=1,
                division='A', profile_photo=photo,
            )
            faculty = Faculty.objects.create(
                faculty_id='TEST-FACULTY', full_name='System Test Faculty',
                email='system.test.faculty@example.com', department='Testing', designation='Tester',
            )
            attendance = Attendance.objects.create(
                student=student, date=date.today(), time=time(9, 0), status=Attendance.Status.PRESENT,
                recognition_method=Attendance.RecognitionMethod.MANUAL,
            )
            face_data = FaceData.objects.create(student=student, face_embedding=[0.1, 0.2], model_name='SFace')
            modification = AttendanceModification.objects.create(
                attendance=attendance, faculty=faculty, previous_status=Attendance.Status.NOT_MARKED,
                new_status=Attendance.Status.PRESENT, reason='System verification',
            )

            self.assertTrue(student.profile_photo.storage.exists(student.profile_photo.name))
            self.assertEqual(face_data.student, student)
            self.assertEqual(modification.attendance, attendance)

# Create your tests here.
