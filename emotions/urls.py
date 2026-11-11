from django.urls import path
from . import views, api_views

urlpatterns = [
    # Endpoints REST API para Next.js / Clientes desacoplados
    path("api/detectar/", api_views.DetectarFrameAPIView.as_view(), name="api_detectar"),
    path("api/historial/", api_views.HistorialAPIView.as_view(), name="api_historial"),
    path("api/estadisticas/", api_views.EstadisticasAPIView.as_view(), name="api_estadisticas"),

    # Vistas clásicas Django (templates) conservadas para compatibilidad
    path("", views.index, name="index"),
    path("video_feed/", views.video_feed, name="video_feed"),
    path("estado/", views.estado, name="estado"),
    path("subir/", views.subir, name="subir"),
    path("historial/", views.historial, name="historial"),
]
