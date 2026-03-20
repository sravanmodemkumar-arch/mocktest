from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("", include("apps.auth_views.urls")),
    path("", include("apps.home.urls")),
    path("", include("apps.exec.urls")),
]

if settings.DEBUG:
    urlpatterns += [path("", include("apps.mock_auth.urls"))]
