from django.db import models


class RegistroEmocion(models.Model):
    ORIGENES = [("camara", "Cámara en vivo"), ("imagen", "Imagen subida")]

    emocion = models.CharField(max_length=20)
    confianza = models.FloatField()
    origen = models.CharField(max_length=10, choices=ORIGENES, default="camara")
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.emocion} ({self.confianza:.0%})"
