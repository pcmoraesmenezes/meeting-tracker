from django.urls import path
from . import views

urlpatterns = [
    path('tracker/', views.tracker_form_view, name='tracker_form'),
    path('success/', views.tracker_success_view, name='tracker_success'),
]
