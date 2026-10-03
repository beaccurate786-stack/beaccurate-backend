from django.shortcuts import render


def home(request):
    """Display the attendance system landing page."""
    return render(request, 'attendance/home.html')

# Create your views here.
