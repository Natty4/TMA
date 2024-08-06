from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='landing_page'),
    # path('book_appointment/', views.book_appointment_page, name='book_appointment_page'),
    path('feedback/', views.feedback_page, name='feedback_page'),
    # path('get_categories/', views.get_categories, name='get_categories'),
    path('get_services/', views.get_services, name='get_services'),
    path('get_doctors/', views.get_doctors, name='get_doctors'),
    path('get_completed_appointments/', views.get_completed_appointments, name='get_completed_appointments'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    # path('book_appointment/', views.book_appointment, name='book_appointment'),
    path('book_appointment/', views.book_appointment, name='book_appointment'),
    path('appointment_success/', views.appointment_success, name='appointment_success'),
  
]




 
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.index, name='index'),
#     path('get_services/', views.get_services, name='get_services'),
#     path('book_appointment/', views.book_appointment, name='book_appointment'),
# ]