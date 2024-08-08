from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='landing_page'),
    path('feedback/', views.feedback_page, name='feedback_page'),
    # path('get_categories/', views.get_categories, name='get_categories'),
    path('get_services/', views.get_services, name='get_services'),
    path('get_doctors/', views.get_doctors, name='get_doctors'),
    path('get_completed_appointments/', views.get_completed_appointments, name='get_completed_appointments'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    
    path('book_appointment_step1/', views.book_appointment_step1, name='book_appointment_step1'),
    path('book_appointment_step2/', views.book_appointment_step2, name='book_appointment_step2'),
    path('book_appointment/', views.book_appointment, name='book_appointment'),
    path('appointment_summary/', views.appointment_summary, name='appointment_summary'),
    path('appointment_success/', views.appointment_success, name='appointment_success'),
    
    path('generate_invoice/', views.generate_invoice, name='generate_invoice'),
    
  
]

