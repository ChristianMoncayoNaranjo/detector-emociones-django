import base64
import os
import time

import cv2
import numpy as np
from django.conf import settings
from django.db import connection
from django.db.models import Avg, Count
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render

from .detector import ETIQUETAS, get_detector
from .models import RegistroEmocion

# Estado compartido con lo ultimo detectado en el video en vivo
ESTADO = {"detecciones": [], "fps": 0.0}


def index(request):
    return render(request, "emotions/index.html")


def _frame_error(texto):
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(img, texto, (30, 240), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (255, 255, 255), 2)
    ok, buf = cv2.imencode(".jpg", img)
    return b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"


def _generar_frames():
    try:
        detector = get_detector()
    except FileNotFoundError:
        yield _frame_error("Falta el modelo: python download_model.py")
        return

    idx = settings.CAMERA_INDEX
    cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW) if os.name == "nt" else cv2.VideoCapture(idx)
    if not cap.isOpened():
        yield _frame_error("No se pudo abrir la camara")
        return

    ultimo_guardado = 0.0
    t_prev = time.time()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)  # efecto espejo
            resultados = detector.detectar(frame)
            detector.dibujar(frame, resultados)

            ahora = time.time()
            ESTADO["fps"] = round(1.0 / max(ahora - t_prev, 1e-6), 1)
            t_prev = ahora
            ESTADO["detecciones"] = [
                {"emocion": r["emocion"], "etiqueta": r["etiqueta"],
                 "confianza": round(r["confianza"], 3)} for r in resultados]

            # Guardar en PostgreSQL maximo cada 2 segundos
            if resultados and ahora - ultimo_guardado >= 2:
                RegistroEmocion.objects.bulk_create([
                    RegistroEmocion(emocion=r["emocion"], confianza=r["confianza"],
                                    origen="camara") for r in resultados])
                ultimo_guardado = ahora

            ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ok:
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                       + buf.tobytes() + b"\r\n")
    finally:
        cap.release()
        ESTADO["detecciones"] = []
        connection.close()


def video_feed(request):
    return StreamingHttpResponse(
        _generar_frames(),
        content_type="multipart/x-mixed-replace; boundary=frame")


def estado(request):
    return JsonResponse(ESTADO)


def subir(request):
    contexto = {}
    if request.method == "POST" and request.FILES.get("imagen"):
        datos = np.frombuffer(request.FILES["imagen"].read(), np.uint8)
        img = cv2.imdecode(datos, cv2.IMREAD_COLOR)
        if img is None:
            contexto["error"] = "El archivo no es una imagen válida."
        else:
            try:
                detector = get_detector()
            except FileNotFoundError as e:
                contexto["error"] = str(e)
                return render(request, "emotions/subir.html", contexto)
            # Reducir imagenes muy grandes
            h, w = img.shape[:2]
            if max(h, w) > 1000:
                f = 1000 / max(h, w)
                img = cv2.resize(img, None, fx=f, fy=f)
            resultados = detector.detectar(img)
            detector.dibujar(img, resultados)
            _, buf = cv2.imencode(".jpg", img)
            contexto["imagen_b64"] = base64.b64encode(buf).decode()
            contexto["resultados"] = resultados
            if resultados:
                RegistroEmocion.objects.bulk_create([
                    RegistroEmocion(emocion=r["emocion"], confianza=r["confianza"],
                                    origen="imagen") for r in resultados])
            else:
                contexto["error"] = "No se detectaron rostros en la imagen."
    return render(request, "emotions/subir.html", contexto)


def historial(request):
    total = RegistroEmocion.objects.count()
    resumen = (RegistroEmocion.objects.values("emocion")
               .annotate(n=Count("id"), prom=Avg("confianza")).order_by("-n"))
    resumen = [{"etiqueta": ETIQUETAS.get(r["emocion"], r["emocion"]),
                "n": r["n"], "prom": r["prom"],
                "pct": round(r["n"] * 100 / total) if total else 0}
               for r in resumen]
    ultimos = list(RegistroEmocion.objects.all()[:20])
    for u in ultimos:
        u.etiqueta = ETIQUETAS.get(u.emocion, u.emocion)
    return render(request, "emotions/historial.html",
                  {"resumen": resumen, "ultimos": ultimos, "total": total})
