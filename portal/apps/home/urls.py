from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_view, name="landing"),
    path("home/", views.home_shell, name="home"),
    path("home/data/", views.home_data, name="home_data"),
    path("home/nav/", views.nav_links, name="nav_links"),
    path("home/profile-menu/", views.profile_menu, name="profile_menu"),
    path("home/notifications/", views.notifications, name="notifications"),
]
