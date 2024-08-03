from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('appointment/', views.appointment, name='appointment'),
    path('get_services/', views.get_services, name='get_services'),
    path('get_doctors/', views.get_doctors, name='get_doctors'),
    path('book_appointment/', views.book_appointment, name='book_appointment'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('get_appointments/<str:email>/', views.get_appointments, name='get_appointments'),
    path('update_appointment_status/<int:appointment_id>/<str:status>/', views.update_appointment_status, name='update_appointment_status'),
    path('cancel_appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
]







 
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.index, name='index'),
#     path('get_services/', views.get_services, name='get_services'),
#     path('book_appointment/', views.book_appointment, name='book_appointment'),
# ]