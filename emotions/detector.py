"""Deteccion de rostros (Haar Cascade de OpenCV) + clasificacion de emociones
(modelo FER+ en formato ONNX, cargado con cv2.dnn)."""
import threading

import cv2
import numpy as np
from django.conf import settings

# Orden de salida del modelo FER+
EMOCIONES = ["neutral", "happiness", "surprise", "sadness",
             "anger", "disgust", "fear", "contempt"]

# Etiquetas ASCII (cv2.putText no soporta tildes)
ETIQUETAS = {
    "neutral": "Neutral", "happiness": "Feliz", "surprise": "Sorpresa",
    "sadness": "Tristeza", "anger": "Enojo", "disgust": "Asco",
    "fear": "Miedo", "contempt": "Desprecio",
}

COLORES = {  # BGR
    "neutral": (200, 200, 200), "happiness": (0, 220, 0),
    "surprise": (0, 220, 220), "sadness": (255, 120, 0),
    "anger": (0, 0, 255), "disgust": (0, 140, 80),
    "fear": (200, 0, 200), "contempt": (0, 128, 255),
}


class DetectorEmociones:
    def __init__(self):
        ruta = settings.MODEL_PATH
        if not ruta.exists():
            raise FileNotFoundError(
                f"No se encontro el modelo en {ruta}. Ejecuta: python download_model.py")
        self.cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.net = cv2.dnn.readNetFromONNX(str(ruta))
        self.lock = threading.Lock()

    def detectar(self, frame):
        """Devuelve lista de dicts: box, emocion, etiqueta, confianza."""
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gris = cv2.equalizeHist(gris)
        rostros = self.cascade.detectMultiScale(
            gris, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        resultados = []
        for (x, y, w, h) in rostros:
            roi = cv2.resize(gris[y:y + h, x:x + w], (64, 64))
            blob = roi.astype(np.float32).reshape(1, 1, 64, 64)
            with self.lock:
                self.net.setInput(blob)
                salida = self.net.forward()[0]
            e = np.exp(salida - salida.max())
            probs = e / e.sum()
            i = int(np.argmax(probs))
            resultados.append({
                "box": (int(x), int(y), int(w), int(h)),
                "emocion": EMOCIONES[i],
                "etiqueta": ETIQUETAS[EMOCIONES[i]],
                "confianza": float(probs[i]),
            })
        return resultados

    @staticmethod
    def dibujar(frame, resultados):
        for r in resultados:
            x, y, w, h = r["box"]
            color = COLORES[r["emocion"]]
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            texto = f'{r["etiqueta"]} {r["confianza"]:.0%}'
            cv2.rectangle(frame, (x, y - 28), (x + w, y), color, -1)
            cv2.putText(frame, texto, (x + 5, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        return frame


_detector = None
_lock = threading.Lock()


def get_detector():
    global _detector
    with _lock:
        if _detector is None:
            _detector = DetectorEmociones()
    return _detector
