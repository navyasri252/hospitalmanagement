from django.contrib import admin
from .models import Doctor, Patient, Appointment, MedicalReport

admin.site.site_header = 'Hospital Management'
admin.site.site_title = 'Hospital Management Admin'
admin.site.index_title = 'Hospital Management Dashboard'


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'specialization', 'consultation_fee', 'available_days', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('name', 'specialization')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'time_slot', 'status', 'created_at')
    list_filter = ('status', 'appointment_date', 'doctor__department')
    search_fields = ('patient__name', 'patient__phone', 'doctor__name')
    actions = ['confirm_appointments', 'cancel_appointments']

    def confirm_appointments(self, request, queryset):
        queryset.update(status='CONFIRMED')
        self.message_user(request, 'Selected appointments were confirmed.')
    confirm_appointments.short_description = 'Confirm selected appointments'

    def cancel_appointments(self, request, queryset):
        queryset.update(status='CANCELLED')
        self.message_user(request, 'Selected appointments were cancelled.')
    cancel_appointments.short_description = 'Cancel selected appointments'


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'created_at')
    search_fields = ('appointment__patient__name', 'appointment__doctor__name')
    list_filter = ('created_at',)
