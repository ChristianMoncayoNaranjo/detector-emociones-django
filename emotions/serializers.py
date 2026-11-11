from rest_framework import serializers
from .models import RegistroEmocion
from .detector import ETIQUETAS


class RegistroEmocionSerializer(serializers.ModelSerializer):
    etiqueta = serializers.SerializerMethodField()

    class Meta:
        model = RegistroEmocion
        fields = ["id", "emocion", "etiqueta", "confianza", "origen", "creado"]

    def get_etiqueta(self, obj):
        return ETIQUETAS.get(obj.emocion, obj.emocion)
