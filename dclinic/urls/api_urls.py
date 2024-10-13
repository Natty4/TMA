from django.urls import path
from dclinic.views.api_views import (
    AuserListCreateView,
    BusinessListView,
    BusinessDetailView,
    BusinessServicesView,
    BusinessProfessionalsView,
    BusinessProfessionalAvailabilityView,
    ServiceListView,
    ServiceDetailView,
    ServiceProfessionalsView,
    ProfessionalListView,
    ProfessionalDetailView,
    ProfessionalAvailabilityView,
    AppointmentListView,
    AppointmentCreateView,
    AppointmentDetailView,
    GenerateInvoiceView,
    InvoiceDetailView,
    # generate_invoice
)




urlpatterns = [
    path('users/', AuserListCreateView.as_view(), name='user-list-create'),
    path('businesses/', BusinessListView.as_view(), name='business-list'),
    path('businesses/<int:pk>/', BusinessDetailView.as_view(), name='business-detail'),
    path('businesses/<int:pk>/services/', BusinessServicesView.as_view(), name='business-services'),
    path('businesses/<int:pk>/professionals/', BusinessProfessionalsView.as_view(), name='business-professionals'),
    path('businesses/<int:pk>/professional_availability/', BusinessProfessionalAvailabilityView.as_view(), name='business-professional-availability'),
    path('businesses/<int:pk>/professional_availability/<int:professional_id>/', BusinessProfessionalAvailabilityView.as_view(), name='business-professional-availability'),

    path('services/', ServiceListView.as_view(), name='service-list'),
    path('services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    path('services/<int:pk>/professionals/', ServiceProfessionalsView.as_view(), name='service-professionals'),

    path('professionals/', ProfessionalListView.as_view(), name='professional-list'),
    path('professionals/<int:pk>/', ProfessionalDetailView.as_view(), name='professional-detail'),
    path('professionals/<int:pk>/availability/', ProfessionalAvailabilityView.as_view(), name='professional-availability'),

    path('appointments/', AppointmentListView.as_view(), name='appointment-list'),
    path('appointments/schedule/', AppointmentCreateView.as_view(), name='appointment-create'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    
    path('appointments/<int:appointment_id>/generate-invoice/', GenerateInvoiceView.as_view(), name='generate-invoice'),
    path('appointments/<int:appointment_id>/invoice/', InvoiceDetailView.as_view(), name='invoice-detail'),
    # path('generate_invoice/', views.generate_invoice, name='generate_invoice'),
]
