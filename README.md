
#  Detector de Emociones en Tiempo Real

> Aplicación web full-stack para **detección y clasificación de emociones faciales** en tiempo real, desarrollada con Django, OpenCV, el modelo FER+ (ONNX) y una interfaz cinematográfica de diseño propio.

---

##  Características

| Funcionalidad | Descripción |
|---|---|
|  **Detección en vivo** | Streaming de la cámara web con detección facial y clasificación de emociones fotograma a fotograma |
|  **Análisis de imagen** | Sube cualquier foto y obtén las emociones detectadas con porcentaje de confianza |
|  **Historial** | Registro persistente de todas las detecciones con estadísticas y distribución |
|  **Modelo FER+** | Clasificación de 8 emociones: Neutral, Feliz, Sorpresa, Tristeza, Enojo, Asco, Miedo y Desprecio |
|  **API REST** | Endpoints Django REST Framework para integración con frontends desacoplados (Next.js, React, etc.) |
|  **Diseño cinematográfico** | Interfaz inspirada en Nexo — fondo crema `#fbf8ef`, tipografías Space Grotesk y DM Sans |

---

##  Stack Tecnológico

**Backend**
- Python 3.10+
- Django 5.x + Django REST Framework
- OpenCV 4.x — detección de rostros con Haar Cascades
- Modelo FER+ ONNX — clasificación de emociones
- PostgreSQL (producción) / SQLite (desarrollo rápido)
- psycopg2, python-dotenv, django-cors-headers

**Frontend**
- HTML5, CSS3 (diseño propio sin frameworks externos en las vistas Django)
- Google Fonts: Space Grotesk 700 & DM Sans 400/500

---

##  Estructura del Proyecto

```
detector-emociones-django-main/
│
├── config/                     # Configuración central de Django
│   ├── settings.py             # Settings (DB, DRF, CORS, rutas)
│   ├── urls.py                 # URL raíz
│   └── wsgi.py
│
├── emotions/                   # Aplicación principal
│   ├── templates/emotions/     # Vistas HTML
│   │   ├── index.html          # Hero cinematográfica con cámara en vivo
│   │   ├── subir.html          # Subida y análisis de imagen
│   │   └── historial.html      # Registros y estadísticas
│   ├── detector.py             # Lógica de detección (Haar + FER+ ONNX)
│   ├── models.py               # Modelo RegistroEmocion (Django ORM)
│   ├── views.py                # Vistas clásicas Django
│   ├── api_views.py            # Endpoints REST (DRF)
│   ├── serializers.py          # Serializadores DRF
│   └── urls.py                 # Rutas de la app
│
├── models_ia/                  # Carpeta del modelo de IA
│   └── emotion-ferplus-8.onnx  # Descargado con download_model.py
│
├── download_model.py           # Script para descargar el modelo FER+ (~34 MB)
├── manage.py
├── requirements.txt
├── .env.example                # Plantilla de variables de entorno
└── .gitignore
```

---

##  Guía de Instalación y Ejecución

### Requisitos previos

Antes de comenzar asegúrate de tener instalado:

- **Python 3.10 o superior** → https://www.python.org/downloads/
- **Git** → https://git-scm.com/
- **PostgreSQL** (opcional, para producción) → https://www.postgresql.org/download/
  - Para desarrollo rápido puedes usar **SQLite** sin instalación adicional.

---

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/detector-emociones-django-main.git
cd detector-emociones-django-main
```

---

### Paso 2 — Crear y activar el entorno virtual

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### Paso 3 — Instalar dependencias

```bash
pip install -r requirements.txt
```

---

### Paso 4 — Configurar las variables de entorno

Copia el archivo de ejemplo y edítalo:

```bash
cp .env.example .env
```

Abre `.env` y ajusta los valores según tu entorno:

```env
DJANGO_SECRET_KEY=cambia-esta-clave-por-una-larga-y-secreta
DJANGO_DEBUG=True

# --- Base de datos ---
# Para desarrollo rápido con SQLite (sin PostgreSQL):
USE_SQLITE=1

# Para PostgreSQL en producción, usa USE_SQLITE=0 y completa:
DB_NAME=emociones_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

# Índice de la cámara web (0 = cámara por defecto del sistema)
CAMERA_INDEX=0
```

> **Nota:** Si usas `USE_SQLITE=1` puedes saltarte la instalación de PostgreSQL y continuar directamente con SQLite.

---

### Paso 5 — Descargar el modelo de IA

El modelo FER+ ONNX (~34 MB) no se incluye en el repositorio. Descárgalo con:

```bash
python download_model.py
```

Esto descargará automáticamente `emotion-ferplus-8.onnx` dentro de la carpeta `models_ia/`.

---

### Paso 6 — Crear la base de datos y aplicar migraciones

```bash
python manage.py migrate
```

---

### Paso 7 — Iniciar el servidor de desarrollo

```bash
python manage.py runserver
```

Abre tu navegador en **http://127.0.0.1:8000/** y ya puedes usar la aplicación. 🎉

---

##  Endpoints de la API REST

La aplicación expone una API REST compatible con cualquier cliente (Next.js, React, apps móviles, etc.):

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/detectar/` | Detectar emociones en un frame Base64 o imagen multipart |
| `GET` | `/api/historial/` | Listar últimos 50 registros de detecciones |
| `GET` | `/api/estadisticas/` | Resumen estadístico: distribución y porcentajes |

### Ejemplo: detectar emoción enviando un frame en Base64

```bash
curl -X POST http://127.0.0.1:8000/api/detectar/ \
  -H "Content-Type: application/json" \
  -d '{"frame": "<base64_del_frame>", "guardar": false}'
```

### Ejemplo: subir imagen como archivo

```bash
curl -X POST http://127.0.0.1:8000/api/detectar/ \
  -F "imagen=@foto.jpg" \
  -F "guardar=true" \
  -F "retornar_imagen=true"
```

---

##  Emociones Detectadas

El modelo FER+ clasifica las siguientes 8 categorías:

| Emoción | Etiqueta |
|---------|----------|
| 😐 neutral | Neutral |
| 😄 happiness | Feliz |
| 😲 surprise | Sorpresa |
| 😢 sadness | Tristeza |
| 😠 anger | Enojo |
| 🤢 disgust | Asco |
| 😨 fear | Miedo |
| 😒 contempt | Desprecio |

---

##  Configuración Avanzada con PostgreSQL

Si deseas usar PostgreSQL en lugar de SQLite:

1. Crea la base de datos en PostgreSQL:
```sql
CREATE DATABASE emociones_db;
```

2. En `.env` establece `USE_SQLITE=0` y completa las credenciales de tu servidor PostgreSQL.

3. Ejecuta las migraciones:
```bash
python manage.py migrate
```

---

##  `requirements.txt`

```
Django>=4.2,<6.0
opencv-python>=4.8,<5.0
numpy>=1.24
psycopg2-binary>=2.9
python-dotenv>=1.0
djangorestframework>=3.14.0
django-cors-headers>=4.3.0
```

---

