from django.urls import path
from . import views

app_name = 'hospital'

urlpatterns = [
    path('', views.DoctorListView.as_view(), name='doctor_list'),
    path('doctor/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
    path('book/<int:pk>/', views.AppointmentCreateView.as_view(), name='book_appointment'),
    path('dashboard/', views.PatientDashboardView.as_view(), name='patient_dashboard'),
    path('admin-appointments/', views.AdminAppointmentListView.as_view(), name='admin_appointments'),
    path('admin-status/<int:pk>/', views.AdminStatusUpdateView.as_view(), name='admin_status_update'),
    path('success/', views.SuccessView.as_view(), name='success'),
]
