from django.urls import path
from . import views

urlpatterns = [
    path("home/",        views.home_shell, name="home"),
    path("home/data/",   views.home_data,  name="home_data"),
    path("home/nav/",    views.nav_links,  name="nav_links"),
    path("",             views.home_shell, name="root"),    # redirect / → /home/ via shell
]
