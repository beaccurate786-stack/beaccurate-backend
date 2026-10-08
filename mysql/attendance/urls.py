from django.urls import path

from . import views

app_name = 'attendance'

urlpatterns = [
    path('log/', views.home, name='log'),
]
