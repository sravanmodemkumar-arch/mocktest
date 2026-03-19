from django.urls import path
from . import views

urlpatterns = [
    path("home/",        views.home_shell, name="home"),
    path("home/data/",   views.home_data,  name="home_data"),
    path("nav/links/",   views.nav_links,  name="nav_links"),
    path("",             views.home_shell, name="root"),    # redirect / → /home/ via shell
]
