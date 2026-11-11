import base64
import cv2
import numpy as np
from django.db.models import Avg, Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .detector import ETIQUETAS, get_detector
from .models import RegistroEmocion
from .serializers import RegistroEmocionSerializer


class DetectarFrameAPIView(APIView):
    """
    Recibe un fotograma o imagen (vía Base64 en JSON o Multipart file 'imagen'),
    detecta los rostros y clasifica las emociones.
    Opcionalmente guarda el registro en la base de datos si 'guardar' = true.
    """
    def post(self, request):
        img = None
        
        # 1. Caso archivo subido multipart (por ejemplo desde input file)
        if "imagen" in request.FILES:
            datos = np.frombuffer(request.FILES["imagen"].read(), np.uint8)
            img = cv2.imdecode(datos, cv2.IMREAD_COLOR)
            origen = "imagen"
        # 2. Caso fotograma en Base64 (ideal para Next.js webcam canvas streaming)
        elif "frame" in request.data:
            frame_str = request.data.get("frame")
            if "," in frame_str:
                frame_str = frame_str.split(",", 1)[1]
            try:
                raw_bytes = base64.b64decode(frame_str)
                datos = np.frombuffer(raw_bytes, np.uint8)
                img = cv2.imdecode(datos, cv2.IMREAD_COLOR)
                origen = request.data.get("origen", "camara")
            except Exception as e:
                return Response(
                    {"error": f"Base64 inválido: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "Se requiere el campo 'imagen' (archivo) o 'frame' (base64)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if img is None:
            return Response(
                {"error": "No se pudo decodificar la imagen proporcionada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            detector = get_detector()
        except FileNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Redimensionar imágenes enormes para acelerar inferencia
        h, w = img.shape[:2]
        if max(h, w) > 1000:
            scale = 1000 / max(h, w)
            img = cv2.resize(img, None, fx=scale, fy=scale)
            h, w = img.shape[:2]

        resultados = detector.detectar(img)

        # Si el cliente solicita guardar en BD (o por defecto si es imagen completa)
        guardar = request.data.get("guardar", True)
        if guardar and resultados:
            RegistroEmocion.objects.bulk_create([
                RegistroEmocion(
                    emocion=r["emocion"],
                    confianza=r["confianza"],
                    origen=origen
                ) for r in resultados
            ])

        # Opcionalmente devolver la imagen con recuadros dibujados
        retornar_imagen = request.data.get("retornar_imagen", False)
        imagen_anotada_b64 = None
        if retornar_imagen:
            detector.dibujar(img, resultados)
            _, buf = cv2.imencode(".jpg", img)
            imagen_anotada_b64 = base64.b64encode(buf).decode()

        return Response({
            "dimensiones": {"ancho": w, "alto": h},
            "cantidad_rostros": len(resultados),
            "detecciones": resultados,
            "imagen_anotada": f"data:image/jpeg;base64,{imagen_anotada_b64}" if imagen_anotada_b64 else None
        }, status=status.HTTP_200_OK)


class HistorialAPIView(APIView):
    """
    Retorna la lista de detecciones recientes o paginadas.
    """
    def get(self, request):
        registros = RegistroEmocion.objects.all()[:50]
        serializer = RegistroEmocionSerializer(registros, many=True)
        return Response(serializer.data)


class EstadisticasAPIView(APIView):
    """
    Retorna el resumen estadístico de las emociones registradas en PostgreSQL/SQLite.
    """
    def get(self, request):
        total = RegistroEmocion.objects.count()
        resumen = (
            RegistroEmocion.objects.values("emocion")
            .annotate(n=Count("id"), prom=Avg("confianza"))
            .order_by("-n")
        )
        resumen_formateado = [
            {
                "emocion": r["emocion"],
                "etiqueta": ETIQUETAS.get(r["emocion"], r["emocion"]),
                "cantidad": r["n"],
                "confianza_promedio": round(r["prom"] * 100, 1) if r["prom"] else 0,
                "porcentaje": round(r["n"] * 100 / total, 1) if total else 0
            }
            for r in resumen
        ]
        return Response({
            "total_registros": total,
            "distribucion": resumen_formateado
        })
