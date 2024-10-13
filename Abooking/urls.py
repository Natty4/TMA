"""
URL configuration for Abooking project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("dclinic.urls.api_urls")),
    path("", include("dclinic.urls.mini_app_urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

