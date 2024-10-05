from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('tracker/', views.tracker_form_view, name='tracker_form'),
    path('success/', views.tracker_success_view, name='tracker_success'),
    path('login/', auth_views.LoginView.as_view(template_name='tracker_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('select_client/', views.select_client_view, name='select_client'),
    path('client_data/<str:client_name>/', views.client_data_view, name='client_data'),
    path('edit_entry/<str:client_name>/<int:entry_id>/', views.edit_entry_view, name='edit_entry'),
]
