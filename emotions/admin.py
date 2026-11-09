from django.contrib import admin

from .models import RegistroEmocion


@admin.register(RegistroEmocion)
class RegistroEmocionAdmin(admin.ModelAdmin):
    list_display = ("emocion", "confianza", "origen", "creado")
    list_filter = ("emocion", "origen")
