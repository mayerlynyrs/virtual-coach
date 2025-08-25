# 🏋️‍♂️ Virtual Coach

**Virtual Coach** es una aplicación inteligente de entrenamiento que combina visión por computadora, feedback por voz y datos fisiológicos (como ritmo cardíaco) para ayudarte a entrenar de forma segura, eficiente y personalizada. Actúa como un entrenador personal virtual que te guía en tiempo real.

---

# 📦 Instalación

Clona este repositorio:

```
git clone https://github.com/mayerlynyrs/virtual-coach.git
cd virtual-coach
```

Crea un entorno virtual (opcional pero recomendado):

```
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

Instala las dependencias:

`pip install -r requirements.txt`

🧪 Ejecución del Proyecto

Ejecuta el sistema principal:

`python main.py`

---

## 📌 Tabla de Contenidos

- [🎯 Objetivo General](#-objetivo-general)
- [🚀 Funcionalidades Principales](#-funcionalidades-principales)
- [🧠 Tecnologías Usadas](#-tecnologías-usadas)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [📦 Instalación](#-instalación)
- [🧪 Ejecución del Proyecto](#-ejecución-del-proyecto)
- [📅 Roadmap](#-roadmap)
- [🤝 Contribuciones](#-contribuciones)
- [📄 Licencia](#-licencia)

---

## 🎯 Objetivo General

Desarrollar un sistema inteligente de entrenamiento personal que permita al usuario:

- Planificar y registrar sus rutinas de ejercicio.
- Usar la cámara para detectar y corregir su postura durante los ejercicios.
- Contar repeticiones automáticamente con base en su movimiento.
- Dar retroalimentación por voz en tiempo real.
- *(Opcional)* Integrar datos desde un smartwatch (Mi Watch XMWTCL02) mediante Google Fit.

---

## 🚀 Funcionalidades Principales

- ✅ Detección de postura mediante MediaPipe y OpenCV.
- ✅ Conteo automático de repeticiones con lógica por ángulos.
- ✅ Feedback de voz mediante `pyttsx3` o `gTTS`.
- ✅ Registro de ejercicios realizados y progreso diario.
- 🔄 Integración con Google Fit para datos fisiológicos.
- 📊 Interfaz para visualizar estadísticas y rendimiento.

---

## 🧠 Tecnologías Usadas

### 🖥️ Backend y Core

- `Python`
- `OpenCV`
- `MediaPipe`
- `NumPy`
- `pyttsx3` o `gTTS`
- `sounddevice` o `pygame` (para feedback sonoro adicional)

### 💻 Interfaz

- `Tkinter` o `PyQt` (Escritorio)
- `Streamlit` (Versión Web local)

### 📱 Wearables

- Google Fit API (acceso indirecto a Mi Watch)
- JSON export desde Mi Fitness app (si aplica)

---

## 📁 Estructura del Proyecto

```bash
virtual-coach/
│
├── core/                      # Lógica principal del entrenamiento
│   ├── pose_estimation.py     # Detección de postura con MediaPipe
│   ├── rep_counter.py         # Lógica para contar repeticiones
│   ├── angle_utils.py         # Cálculo de ángulos entre articulaciones
│   └── feedback_audio.py      # Voz y retroalimentación sonora
│
├── interface/                 # Interfaz de usuario (UI)
│   ├── gui_tkinter.py         # Interfaz con Tkinter
│   ├── web_streamlit.py       # Interfaz web con Streamlit
│   └── assets/                # Iconos, sonidos, imágenes, etc.
│
├── data/                      # Almacenamiento de estadísticas y sesiones
│   ├── logs/
│   └── user_sessions.json
│
├── smartwatch_integration/    # API y herramientas para Google Fit
│   └── google_fit_api.py
│
├── tests/                     # Scripts de pruebas unitarias
│   └── test_pose_estimation.py
│
├── README.md                  # Este archivo
├── requirements.txt           # Dependencias del proyecto
├── main.py                    # Script principal para correr el sistema
└── LICENSE                    # Licencia del proyecto (MIT)
```

### Construir la imagen Docker:
En la terminal, navega al directorio donde se encuentra el Dockerfile y ejecuta el siguiente comando para construir la imagen:

`docker build -t virtual-coach .`


Esto descargará la imagen base de Python, instalará las dependencias de tu requirements.txt y copiará los archivos de tu proyecto al contenedor.

### Ejecutar el contenedor:
Una vez construida la imagen, puedes ejecutar el contenedor con el siguiente comando:

`docker run --rm -it --device=/dev/video0 virtual-coach`


--device=/dev/video0 es importante para que Docker pueda acceder a tu cámara. Si usas Windows, esto podría ser diferente, y necesitas verificar cómo Docker maneja el acceso a dispositivos en tu sistema. En sistemas Windows, puedes intentar --privileged o revisar la configuración de Docker para acceder a dispositivos.

### Acceder a la cámara en Docker en Windows:
En Windows, Docker corre dentro de una máquina virtual, lo que puede hacer que el acceso a la cámara sea un poco más complicado. Aquí hay algunas opciones para que Docker pueda acceder a la cámara:

Habilitar dispositivos de cámara USB en Docker: Puedes intentar configurar Docker para usar dispositivos específicos de la cámara. Asegúrate de que Docker Desktop esté ejecutándose en modo WSL 2 si estás en Windows 11, ya que esto puede mejorar la compatibilidad con dispositivos.

Probar con --privileged: A veces, Docker necesita privilegios adicionales para acceder a dispositivos. Puedes probar ejecutando con --privileged:

`docker run --rm -it --privileged virtual-coach`

### Alternativa: Docker Compose

`docker-compose up --build`

