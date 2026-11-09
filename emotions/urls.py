from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("video_feed/", views.video_feed, name="video_feed"),
    path("estado/", views.estado, name="estado"),
    path("subir/", views.subir, name="subir"),
    path("historial/", views.historial, name="historial"),
]
