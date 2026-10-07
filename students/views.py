from rest_framework import viewsets
from .access import filter_students_for
from .models import Student
from .serializers import StudentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get_queryset(self):
        return filter_students_for(self.request.user, super().get_queryset())
