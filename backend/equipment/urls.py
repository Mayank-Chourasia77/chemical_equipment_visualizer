from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_csv, name='upload_csv'),
    path('latest/', views.get_latest, name='get_latest'),
    path('history/', views.get_history, name='get_history'),
    path('pdf/', views.generate_pdf, name='generate_pdf'),
]
