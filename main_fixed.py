import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import math
import threading
import time

# Configurar OpenCV para usar el backend correcto
cv2.setUseOptimized(True)

# Inicializar TTS en un hilo separado para evitar bloqueos
class TTSManager:
    def __init__(self):
        self.engine = None
        self.initialize_tts()
        
    def initialize_tts(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 160)
            # Configurar voz en español si está disponible
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            print("TTS inicializado correctamente")
        except Exception as e:
            print(f"Error inicializando TTS: {e}")
            self.engine = None
    
    def speak(self, text):
        if self.engine:
            def _speak():
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"Error en TTS: {e}")
            
            # Ejecutar TTS en hilo separado para no bloquear
            thread = threading.Thread(target=_speak, daemon=True)
            thread.start()
        else:
            print(f"TTS no disponible: {text}")

# Inicializar TTS Manager
tts_manager = TTSManager()

# Inicializar MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Función para calcular el ángulo entre tres puntos
def calculate_angle(a, b, c):
    """
    Calcula el ángulo entre tres puntos
    a: punto superior (cadera)
    b: punto medio (rodilla)
    c: punto inferior (tobillo)
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])
    
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    
    return angle

# Inicializar variables
counter = 0
stage = None  # "arriba" o "abajo"
last_speak_time = 0
speak_cooldown = 2.0  # Cooldown de 2 segundos entre anuncios

def main():
    global counter, stage, last_speak_time
    
    print("Iniciando aplicación...")
    print("Presiona 'q' para salir")
    
    # Intentar diferentes índices de cámara
    camera_found = False
    cap = None
    
    for camera_index in [0, 1, 2]:
        try:
            print(f"Probando cámara índice {camera_index}...")
            cap = cv2.VideoCapture(camera_index)
            
            if cap is not None and cap.isOpened():
                # Probar leer un frame
                ret, frame = cap.read()
                if ret and frame is not None:
                    camera_found = True
                    print(f"Cámara encontrada en índice {camera_index}")
                    break
                else:
                    cap.release()
            else:
                if cap:
                    cap.release()
        except Exception as e:
            print(f"Error con cámara índice {camera_index}: {e}")
            if cap:
                cap.release()
    
    if not camera_found:
        print("ERROR: No se pudo acceder a ninguna cámara")
        print("Verifica que:")
        print("- La cámara esté conectada")
        print("- No esté siendo usada por otra aplicación")
        print("- Tengas permisos para usar la cámara")
        return
    
    # Configurar resolución de cámara
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("Inicializando MediaPipe...")
    
    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=1  # Usar modelo más ligero
    ) as pose:
        
        print("¡Aplicación lista! Ventana de video abriéndose...")
        
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                print("No se pudo leer frame de la cámara")
                break
            
            frame_count += 1
            
            # Voltear imagen horizontalmente para efecto espejo
            frame = cv2.flip(frame, 1)
            
            # Convertir BGR a RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            # Hacer detección de pose
            results = pose.process(image)
            
            # Volver a BGR para OpenCV
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Dibujar las poses detectadas
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, 
                    results.pose_landmarks, 
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2)
                )
                
                try:
                    landmarks = results.pose_landmarks.landmark
                    
                    # Obtener coordenadas de cadera, rodilla y tobillo derechos
                    hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                    knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                    ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                             landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
                    
                    # Calcular ángulo
                    angle = calculate_angle(hip, knee, ankle)
                    
                    # Mostrar ángulo en pantalla
                    cv2.putText(image, f'Angulo: {int(angle)}°',
                                (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    
                    # Lógica de conteo de sentadillas
                    current_time = time.time()
                    
                    if angle < 90:  # Posición abajo
                        stage = "abajo"
                        cv2.putText(image, 'ABAJO', (400, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    if angle > 150 and stage == "abajo":  # Posición arriba
                        stage = "arriba"
                        counter += 1
                        print(f"¡Repetición {counter} completada!")
                        
                        # Anunciar con cooldown para evitar spam
                        if current_time - last_speak_time > speak_cooldown:
                            tts_manager.speak(f"Repetición {counter}")
                            last_speak_time = current_time
                    
                    if stage == "arriba":
                        cv2.putText(image, 'ARRIBA', (400, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Mostrar estado de detección
                    cv2.putText(image, 'Persona detectada', (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                except Exception as e:
                    print(f"Error procesando landmarks: {e}")
                    cv2.putText(image, 'Error en detección', (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                # No se detectó persona
                cv2.putText(image, 'No se detecta persona', (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Dibujar interfaz de contador
            cv2.rectangle(image, (0, 0), (250, 80), (245, 117, 16), -1)
            
            # Título
            cv2.putText(image, 'SENTADILLAS', (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
            # Contador
            cv2.putText(image, f'Reps: {counter}', (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            
            # Instrucciones
            cv2.putText(image, 'Presiona Q para salir', (50, 450),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Mostrar FPS
            cv2.putText(image, f'Frame: {frame_count}', (500, 450),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Mostrar la imagen
            cv2.imshow('Entrenamiento Inteligente - Sentadillas', image)
            
            # Salir con 'q' o ESC
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 27 = ESC
                print("Saliendo...")
                break
    
    # Limpiar
    cap.release()
    cv2.destroyAllWindows()
    print(f"Sesión terminada. Total de repeticiones: {counter}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario")
    except Exception as e:
        print(f"Error general: {e}")
        print("Verifica que tengas todas las librerías instaladas:")
        print("pip install opencv-python mediapipe pyttsx3 numpy")
    finally:
        cv2.destroyAllWindows()
