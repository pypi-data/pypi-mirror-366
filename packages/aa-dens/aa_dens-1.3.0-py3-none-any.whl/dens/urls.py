"""Routes."""

from django.urls import path

from . import views

app_name = "dens"

urlpatterns = [
    path("", views.index, name="index"),
    path("add_owner", views.add_owner, name="add_owner"),
    path("dens", views.dens, name="dens"),
    path("dens_data", views.MercenaryDensListJson.as_view(), name="dens_data"),
]
