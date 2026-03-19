from django.urls import path
from . import views

urlpatterns = [
    path("api/v1/auth/login", views.login, name="mock_login"),
    path("api/v1/auth/me", views.me, name="mock_me"),
    path("api/v1/auth/logout", views.logout, name="mock_logout"),
    path("api/v1/auth/token/refresh", views.token_refresh, name="mock_token_refresh"),
]
