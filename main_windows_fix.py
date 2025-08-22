import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import math
import threading
import time
import platform

# Configurar OpenCV para Windows
if platform.system() == "Windows":
    # Probar diferentes backends para Windows
    cv2.setUseOptimized(True)
    
# Inicializar TTS en un hilo separado
class TTSManager:
    def __init__(self):
        self.engine = None
        self.initialize_tts()
        
    def initialize_tts(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 160)
            # Usar voz en español
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'helena' in voice.name.lower() or 'spanish' in voice.name.lower():
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
            
            thread = threading.Thread(target=_speak, daemon=True)
            thread.start()
        else:
            print(f"TTS no disponible: {text}")

# Función para probar cámara con diferentes configuraciones
def test_camera_advanced(camera_index):
    """Prueba una cámara con diferentes configuraciones para Windows"""
    
    # Lista de backends a probar (específicos para Windows)
    backends_to_try = [
        cv2.CAP_DSHOW,      # DirectShow (recomendado para Windows)
        cv2.CAP_MSMF,       # Microsoft Media Foundation
        cv2.CAP_V4L2,       # Video4Linux2 (por si acaso)
        cv2.CAP_ANY         # Cualquier backend disponible
    ]
    
    for backend in backends_to_try:
        try:
            print(f"  Probando backend {backend} en cámara {camera_index}...")
            cap = cv2.VideoCapture(camera_index, backend)
            
            if cap.isOpened():
                # Configurar propiedades básicas
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reducir buffer para menos latencia
                
                # Intentar leer varios frames (a veces el primero falla)
                success_count = 0
                for attempt in range(5):
                    ret, frame = cap.read()
                    if ret and frame is not None and frame.size > 0:
                        success_count += 1
                    time.sleep(0.1)  # Pequeña pausa entre intentos
                
                if success_count >= 3:  # Al menos 3 de 5 frames exitosos
                    print(f"  ✓ Cámara {camera_index} funciona con backend {backend}")
                    return cap, backend
                else:
                    print(f"  ✗ Cámara {camera_index} con backend {backend}: frames inconsistentes ({success_count}/5)")
                    cap.release()
            else:
                print(f"  ✗ No se puede abrir cámara {camera_index} con backend {backend}")
                cap.release()
                
        except Exception as e:
            print(f"  ✗ Error con backend {backend}: {e}")
            if 'cap' in locals():
                cap.release()
    
    return None, None

# Inicializar componentes
tts_manager = TTSManager()
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    """Calcula el ángulo entre tres puntos"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])
    
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    
    return angle

def main():
    global counter, stage, last_speak_time
    
    counter = 0
    stage = None
    last_speak_time = 0
    speak_cooldown = 2.0
    
    print("=== INICIANDO CONTADOR DE SENTADILLAS ===")
    print("Sistema operativo:", platform.system())
    print("OpenCV versión:", cv2.__version__)
    
    # Buscar cámara con configuración avanzada
    cap = None
    backend_used = None
    camera_found = False
    
    print("\nBuscando cámaras disponibles...")
    
    # Probar múltiples índices de cámara
    for camera_index in range(6):  # Probar índices 0-5
        print(f"\nProbando cámara índice {camera_index}:")
        cap, backend_used = test_camera_advanced(camera_index)
        
        if cap is not None:
            camera_found = True
            print(f"¡Cámara encontrada en índice {camera_index} con backend {backend_used}!")
            break
    
    if not camera_found:
        print("\n❌ ERROR: No se pudo acceder a ninguna cámara")
        print("\nSOLUCIONES PARA WINDOWS:")
        print("1. Abre 'Configuración' → 'Privacidad y seguridad' → 'Cámara'")
        print("2. Asegúrate que 'Acceso a la cámara' esté activado")
        print("3. Permite acceso a aplicaciones de escritorio")
        print("4. Cierra completamente Chrome, Teams, Zoom, etc.")
        print("5. En el Administrador de dispositivos, desinstala y reinstala la cámara")
        print("6. Ejecuta como administrador: 'sfc /scannow' en CMD")
        print("7. Reinicia el servicio de Windows Camera: 'net stop FrameServer' y 'net start FrameServer'")
        
        # Intentar con comando específico de Windows
        print("\n💡 PRUEBA MANUAL:")
        print("Abre la aplicación 'Cámara' de Windows para verificar que funciona")
        print("Si la app Cámara funciona, el problema puede ser permisos de Python")
        
        return
    
    print(f"\n🎥 Cámara inicializada correctamente")
    print("Presiona 'Q' para salir")
    
    # Configuraciones adicionales para estabilidad
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    # Obtener información de la cámara
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Resolución: {width}x{height}, FPS: {fps}")
    
    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=1
    ) as pose:
        
        print("🤖 MediaPipe inicializado")
        print("¡Aplicación lista! Ponte frente a la cámara...")
        
        frame_count = 0
        fps_start_time = time.time()
        actual_fps = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Error leyendo frame. Intentando reconectar...")
                # Intentar reconectar
                cap.release()
                time.sleep(1)
                cap = cv2.VideoCapture(0, backend_used) if backend_used else cv2.VideoCapture(0)
                if not cap.isOpened():
                    print("No se pudo reconectar. Saliendo...")
                    break
                continue
            
            frame_count += 1
            
            # Calcular FPS real
            if frame_count % 30 == 0:
                current_time = time.time()
                elapsed = current_time - fps_start_time
                actual_fps = 30 / elapsed if elapsed > 0 else 0
                fps_start_time = current_time
            
            # Voltear imagen horizontalmente
            frame = cv2.flip(frame, 1)
            
            # Convertir a RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            # Procesar con MediaPipe
            results = pose.process(image)
            
            # Volver a BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Dibujar poses
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
                    
                    # Obtener puntos clave
                    hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                    knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                    ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                             landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
                    
                    angle = calculate_angle(hip, knee, ankle)
                    
                    # Mostrar ángulo
                    cv2.putText(image, f'Angulo: {int(angle)}°',
                                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    
                    # Lógica de conteo
                    current_time = time.time()
                    
                    if angle < 90:
                        stage = "abajo"
                        cv2.putText(image, 'ABAJO', (400, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    if angle > 150 and stage == "abajo":
                        stage = "arriba"
                        counter += 1
                        print(f"🏋️ Repetición {counter} completada!")
                        
                        if current_time - last_speak_time > speak_cooldown:
                            tts_manager.speak(f"Repetición {counter}")
                            last_speak_time = current_time
                    
                    if stage == "arriba":
                        cv2.putText(image, 'ARRIBA', (400, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    cv2.putText(image, '✓ Persona detectada', (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                except Exception as e:
                    print(f"Error procesando pose: {e}")
                    cv2.putText(image, 'Error en pose', (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                cv2.putText(image, 'Colócate frente a la cámara', (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
            
            # Interfaz de usuario
            cv2.rectangle(image, (0, 0), (300, 80), (245, 117, 16), -1)
            cv2.putText(image, 'CONTADOR SENTADILLAS', (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            cv2.putText(image, f'Repeticiones: {counter}', (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Información del sistema
            cv2.putText(image, f'FPS: {actual_fps:.1f}', (width-120, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(image, f'Backend: {backend_used}', (width-200, height-20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            cv2.putText(image, 'Presiona Q para salir', (50, height-20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Mostrar ventana
            cv2.imshow('🏋️ Entrenamiento Inteligente - Sentadillas', image)
            
            # Controles
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q') or key == 27:
                print("👋 Saliendo...")
                break
    
    # Limpieza
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n🎯 Sesión completada!")
    print(f"📊 Total de repeticiones: {counter}")
    print("¡Buen entrenamiento! 💪")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        print("\n🔧 Soluciones:")
        print("1. Ejecuta como administrador")
        print("2. Reinstala OpenCV: pip uninstall opencv-python && pip install opencv-python")
        print("3. Verifica drivers de cámara en Administrador de dispositivos")
    finally:
        cv2.destroyAllWindows()