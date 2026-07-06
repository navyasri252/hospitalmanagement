import json
from datetime import date

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, DetailView
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django import forms

from .models import Doctor, Appointment, Patient, MedicalReport


class AppointmentForm(forms.ModelForm):
    patient_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    patient_phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    patient_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'time_slot', 'reason']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time_slot': forms.HiddenInput(),
            'doctor': forms.HiddenInput(),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')
        time_slot = cleaned_data.get('time_slot')
        if doctor and appointment_date and time_slot:
            if Appointment.objects.filter(doctor=doctor, appointment_date=appointment_date, time_slot=time_slot).exists():
                raise forms.ValidationError('This slot is already booked. Please choose another time.')
        return cleaned_data

    def save(self, commit=True):
        patient_name = self.cleaned_data.get('patient_name')
        patient_phone = self.cleaned_data.get('patient_phone')
        patient_email = self.cleaned_data.get('patient_email', '')

        patient, _ = Patient.objects.get_or_create(name=patient_name, phone=patient_phone)
        if patient_email:
            patient.email = patient_email
            patient.save()

        self.instance.patient = patient
        return super().save(commit=commit)


class DoctorListView(ListView):
    model = Doctor
    template_name = 'hospital/doctor_list.html'
    context_object_name = 'doctors'

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)
        department = self.request.GET.get('department')
        search = self.request.GET.get('search')
        if department:
            queryset = queryset.filter(department=department)
        if search:
            queryset = queryset.filter(name__icontains=search) | queryset.filter(specialization__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Doctor.DEPARTMENTS
        context['selected_department'] = self.request.GET.get('department', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = 'hospital/doctor_detail.html'
    context_object_name = 'doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slots = [
            '09:00 AM - 09:30 AM',
            '10:00 AM - 10:30 AM',
            '11:00 AM - 11:30 AM',
            '02:00 PM - 02:30 PM',
            '03:00 PM - 03:30 PM',
        ]
        upcoming = self.object.appointments.filter(appointment_date__gte=date.today()).order_by('appointment_date', 'time_slot')
        booked = {}
        for appointment in upcoming:
            key = appointment.appointment_date.strftime('%Y-%m-%d')
            booked.setdefault(key, []).append(appointment.time_slot)
        context['slot_choices'] = slots
        context['booked_by_date'] = json.dumps(booked)
        return context


class AppointmentCreateView(CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'hospital/book_appointment.html'
    success_url = reverse_lazy('hospital:success')

    def get_initial(self):
        initial = super().get_initial()
        doctor = get_object_or_404(Doctor, pk=self.kwargs['pk'])
        initial['doctor'] = doctor
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        doctor = get_object_or_404(Doctor, pk=self.kwargs['pk'])
        form.fields['doctor'].initial = doctor
        form.fields['doctor'].queryset = Doctor.objects.filter(pk=doctor.pk)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = get_object_or_404(Doctor, pk=self.kwargs['pk'])
        slots = [
            '09:00 AM - 09:30 AM',
            '10:00 AM - 10:30 AM',
            '11:00 AM - 11:30 AM',
            '02:00 PM - 02:30 PM',
            '03:00 PM - 03:30 PM',
        ]
        upcoming = doctor.appointments.filter(appointment_date__gte=date.today()).order_by('appointment_date', 'time_slot')
        booked = {}
        for appointment in upcoming:
            key = appointment.appointment_date.strftime('%Y-%m-%d')
            booked.setdefault(key, []).append(appointment.time_slot)
        context['doctor'] = doctor
        context['slot_choices'] = slots
        context['booked_by_date'] = json.dumps(booked)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Appointment request submitted successfully.')
        return super().form_valid(form)


class PatientDashboardView(ListView):
    model = Appointment
    template_name = 'hospital/patient_dashboard.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        query = super().get_queryset().order_by('-appointment_date', '-created_at')
        patient_name = self.request.GET.get('patient_name')
        patient_phone = self.request.GET.get('patient_phone')
        if patient_name and patient_phone:
            return query.filter(patient__name__icontains=patient_name, patient__phone__icontains=patient_phone)
        return query.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient_name'] = self.request.GET.get('patient_name', '')
        context['patient_phone'] = self.request.GET.get('patient_phone', '')
        return context


@method_decorator(login_required(login_url=reverse_lazy('admin:login')), name='dispatch')
class AdminAppointmentListView(ListView):
    model = Appointment
    template_name = 'hospital/admin_appointments.html'
    context_object_name = 'appointments'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-appointment_date', 'time_slot')
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        if search:
            queryset = queryset.filter(patient__name__icontains=search) | queryset.filter(doctor__name__icontains=search)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'Staff access required.')
            return redirect(reverse_lazy('admin:login'))
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required(login_url=reverse_lazy('admin:login')), name='dispatch')
class AdminStatusUpdateView(View):
    def post(self, request, pk):
        if not request.user.is_staff:
            messages.error(request, 'Staff access required.')
            return redirect(reverse_lazy('admin:login'))
        appointment = get_object_or_404(Appointment, pk=pk)
        action = request.POST.get('action')
        if action == 'confirm':
            appointment.status = 'CONFIRMED'
        elif action == 'complete':
            appointment.status = 'COMPLETED'
        elif action == 'cancel':
            appointment.status = 'CANCELLED'
        appointment.save()
        messages.success(request, 'Appointment status updated successfully.')
        return redirect(request.META.get('HTTP_REFERER', reverse_lazy('hospital:admin_appointments')))


class SuccessView(TemplateView):
    template_name = 'hospital/success.html'
