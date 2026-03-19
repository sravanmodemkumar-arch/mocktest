from django.urls import path, include

urlpatterns = [
    path("", include("apps.auth_views.urls")),
    path("", include("apps.home.urls")),
]
