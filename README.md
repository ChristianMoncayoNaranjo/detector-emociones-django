# 😀 Detección de Emociones mediante Expresiones Faciales

Aplicativo web desarrollado con **Django + OpenCV + PostgreSQL** que detecta rostros en tiempo real desde la cámara y clasifica la emoción de cada uno (neutral, feliz, sorpresa, tristeza, enojo, asco, miedo, desprecio).

**Universidad Estatal de Milagro (UNEMI)**

## Funcionalidades
- Captura y transmisión de video en tiempo real (streaming MJPEG con OpenCV).
- Detección de rostros con *Haar Cascade* de OpenCV (`cv2.CascadeClassifier`).
- Clasificación de emociones con el modelo **FER+** (ONNX) cargado con `cv2.dnn`.
- Resultados dibujados directamente sobre el video (recuadro, emoción y % de confianza).
- Panel lateral con emociones y FPS en vivo.
- Análisis de imágenes subidas.
- Historial y estadísticas guardados en **PostgreSQL**.

## Requisitos
- Python 3.9 o superior
- PostgreSQL 13 o superior
- Cámara web
- Conexión a internet (solo para instalar librerías y descargar el modelo)

## Instalación

```bash
# 1. Clonar
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO

# 2. Entorno virtual (NO se sube a GitHub)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / Mac

# 3. Dependencias
pip install -r requirements.txt

# 4. Descargar el modelo de emociones (~34 MB)
python download_model.py
```

## Base de datos PostgreSQL
Crear la base de datos (en pgAdmin o en `psql`):
```sql
CREATE DATABASE emociones_db;
```
Copiar `.env.example` a `.env` y poner tu contraseña de PostgreSQL:
```
DB_NAME=emociones_db
DB_USER=postgres
DB_PASSWORD=tu_password
```

## Ejecución
```bash
python manage.py makemigrations emotions
python manage.py migrate
python manage.py runserver
```
Abrir http://127.0.0.1:8000/ y presionar **Iniciar**.

(Opcional) `python manage.py createsuperuser` para entrar a `/admin/`.

## Estructura
```
config/            Configuración de Django
emotions/          App principal
  detector.py      Lógica OpenCV (detección + emociones)
  views.py         Vistas y streaming de video
  models.py        Modelo RegistroEmocion (PostgreSQL)
  templates/       Interfaz web (Bootstrap)
models_ia/         Modelo ONNX (se descarga con download_model.py)
download_model.py  Descarga el modelo
requirements.txt
```

## Problemas comunes
- **No abre la cámara:** cambia `CAMERA_INDEX=1` en `.env`; cierra otras apps que usen la cámara (Zoom, Teams).
- **Falta el modelo:** ejecuta `python download_model.py`.
- **Error de conexión a PostgreSQL:** revisa usuario/contraseña en `.env` y que el servicio esté activo.
- **Prueba rápida sin PostgreSQL:** `USE_SQLITE=1` en `.env` (el entregable debe usar PostgreSQL).

## Integrantes
- Nombre 1
- Nombre 2
