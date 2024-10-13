from django.urls import path
from dclinic.views import mini_app_views as views
urlpatterns = [
    path('', views.home_view, name='home'),
    path('businesses/', views.business_list_view, name='business_list'),
    path('businesses/<int:business_id>/services/', views.service_list_view, name='service_list'),
    path('businesses/<int:business_id>/services/<int:service_id>/', views.service_detail_view, name='service_detail'),
    path('businesses/<int:business_id>/services/<int:service_id>/professionals/<int:professional_id>/booking/<str:date>/<str:time>/', 
         views.booking_form_view, name='booking_form'),
    path('businesses/<int:business_id>/services/<int:service_id>/professionals/<int:professional_id>/booking/<str:date>/<str:time>/summary/', 
         views.booking_summary_view, name='booking_summary'),
    path('thank_you/<int:appointment_id>/', views.thank_you_view, name='thank_you'),
]


