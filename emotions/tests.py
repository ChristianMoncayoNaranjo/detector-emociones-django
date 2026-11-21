import cv2
import numpy as np
from django.test import Client, TestCase


class DetectorEmocionesTests(TestCase):
    def setUp(self):
        self.client = Client()

    # 1. PRUEBA DE INTEGRACIÓN: Validar ruta principal de Django
    def test_ruta_principal_carga_correctamente(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detector de Emociones")

    # 2. PRUEBA DE INTEGRACIÓN: Validar ruta de historial
    def test_ruta_historial_carga_correctamente(self):
        response = self.client.get("/historial/")
        self.assertIn(response.status_code, [200, 302])

    # 3. PRUEBA UNITARIA: Validar procesamiento de imagen con OpenCV
    def test_procesamiento_frame_opencv_valido(self):
        frame_simulado = np.zeros((480, 640, 3), dtype=np.uint8)
        gris = cv2.cvtColor(frame_simulado, cv2.COLOR_BGR2GRAY)

        self.assertEqual(gris.shape, (480, 640))
        self.assertIsNotNone(gris)