"""Descarga el modelo FER+ (ONNX) de emociones faciales a models_ia/."""
import urllib.request
from pathlib import Path

URL = ("https://github.com/onnx/models/raw/main/validated/vision/body_analysis/"
       "emotion_ferplus/model/emotion-ferplus-8.onnx")
DEST = Path(__file__).resolve().parent / "models_ia" / "emotion-ferplus-8.onnx"

if DEST.exists():
    print("El modelo ya existe:", DEST)
else:
    DEST.parent.mkdir(exist_ok=True)
    print("Descargando modelo (~34 MB)...")
    urllib.request.urlretrieve(URL, DEST)
    print("Listo:", DEST)
