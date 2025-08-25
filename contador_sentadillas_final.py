import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import math
import threading
import time

# Configuración específica para solucionar ventanas negras en Windows
cv2.setUseOptimized(True)

# TTS Manager mejorado
class TTSManager:
    def __init__(self):
        self.engine = None
        self.initialize_tts()
        
    def initialize_tts(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 160)
            # Usar voz Helena (español)
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'helena' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            print("✓ TTS inicializado (Helena)")
        except Exception as e:
            print(f"⚠️ TTS error: {e}")
            self.engine = None
    
    def speak(self, text):
        if self.engine:
            def _speak():
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except:
                    pass
            threading.Thread(target=_speak, daemon=True).start()
        else:
            print(f"🔊 {text}")

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
    print("🏋️ CONTADOR DE SENTADILLAS INTELIGENTE")
    print("=" * 50)
    
    # Variables globales
    counter = 0
    stage = None
    last_speak_time = 0
    speak_cooldown = 2.0
    
    print("🎥 Inicializando cámara...")
    
    # Usar la configuración que sabemos que funciona
    cap = cv2.VideoCapture(0)  # DirectShow backend
    
    if not cap.isOpened():
        print("❌ Error: No se pudo abrir la cámara")
        return
    
    # Configurar cámara
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Importante para reducir latencia
    
    print("✓ Cámara inicializada correctamente")
    
    # Verificar que podemos leer frames
    print("🔍 Verificando lectura de frames...")
    test_ret, test_frame = cap.read()
    if not test_ret or test_frame is None:
        print("❌ Error: No se pueden leer frames de la cámara")
        cap.release()
        return
    
    print(f"✓ Frames OK - Resolución: {test_frame.shape[1]}x{test_frame.shape[0]}")
    
    print("🤖 Inicializando MediaPipe...")
    
    with mp_pose.Pose(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        model_complexity=1
    ) as pose:
        
        print("✅ ¡Todo listo!")
        print("📋 INSTRUCCIONES:")
        print("   • Ponte frente a la cámara")
        print("   • Haz sentadillas completas")
        print("   • Presiona 'Q' para salir")
        print("   • Presiona 'R' para reiniciar contador")
        print("\n🎯 ¡Comenzando en 3 segundos!")
        
        # Countdown
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        
        print("🚀 ¡EMPEZAMOS!")
        
        # Variables para FPS y estadísticas
        frame_count = 0
        fps_start_time = time.time()
        actual_fps = 0
        
        # Crear ventana con configuración específica para Windows
        window_name = 'Contador de Sentadillas - Presiona Q para salir'
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)  # Mantener al frente
        
        while True:
            ret, frame = cap.read()
            
            if not ret or frame is None:
                print("⚠️ Error leyendo frame, reintentando...")
                continue
            
            frame_count += 1
            
            # Calcular FPS cada 30 frames
            if frame_count % 30 == 0:
                current_time = time.time()
                elapsed = current_time - fps_start_time
                actual_fps = 30 / elapsed if elapsed > 0 else 0
                fps_start_time = current_time
            
            # Voltear horizontalmente para efecto espejo
            frame = cv2.flip(frame, 1)
            
            # Asegurar que el frame no esté vacío
            if frame.size == 0:
                continue
            
            # Convertir color para MediaPipe
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            # Procesar pose
            results = pose.process(image)
            
            # Volver a BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Verificar que la imagen se convirtió correctamente
            if image is None or image.size == 0:
                continue
            
            # Dibujar conexiones de pose
            if results.pose_landmarks:
                # Dibujar esqueleto
                mp_drawing.draw_landmarks(
                    image, 
                    results.pose_landmarks, 
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=3)
                )
                
                try:
                    landmarks = results.pose_landmarks.landmark
                    
                    # Obtener coordenadas (usar lado derecho)
                    hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                    knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                    ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                             landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
                    
                    # Calcular ángulo
                    angle = calculate_angle(hip, knee, ankle)
                    
                    # Mostrar ángulo
                    cv2.putText(image, f'Angulo Rodilla: {int(angle)}°',
                                (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    
                    # Lógica de conteo de sentadillas
                    current_time = time.time()
                    
                    # Detectar posición baja (sentadilla)
                    if angle < 90:
                        stage = "abajo"
                        cv2.putText(image, 'POSICION: ABAJO', (30, 90),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
                    # Detectar posición alta (de pie) - contar repetición
                    if angle > 150 and stage == "abajo":
                        stage = "arriba"
                        counter += 1
                        print(f"🏋️ ¡Repetición {counter} completada! Ángulo: {int(angle)}°")
                        
                        # Anunciar con TTS (con cooldown)
                        if current_time - last_speak_time > speak_cooldown:
                            tts_manager.speak(f"Repetición {counter}")
                            last_speak_time = current_time
                    
                    # Mostrar estado actual
                    if stage == "arriba" or stage is None:
                        cv2.putText(image, 'POSICION: ARRIBA', (30, 90),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Indicador de detección
                    cv2.putText(image, '✓ Persona detectada', (30, 130),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                except Exception as e:
                    print(f"Error procesando pose: {e}")
                    cv2.putText(image, 'Error en detección de pose', (30, 130),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                # No se detectó persona
                cv2.putText(image, 'Colócate frente a la cámara', (30, 130),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
                cv2.putText(image, 'Asegúrate de estar completamente visible', (30, 160),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 2)
            
            # Panel de información (fondo semi-transparente)
            overlay = image.copy()
            cv2.rectangle(overlay, (0, 0), (400, 200), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
            
            # Título principal
            cv2.putText(image, 'CONTADOR DE SENTADILLAS', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Contador grande y visible
            cv2.putText(image, f'REPETICIONES: {counter}', (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
            
            # Información adicional
            cv2.putText(image, f'FPS: {actual_fps:.1f}', (10, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Controles
            cv2.putText(image, 'Controles: Q=Salir | R=Reiniciar', (10, image.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # MOSTRAR IMAGEN - ¡ESTO ES LO MÁS IMPORTANTE!
            cv2.imshow(window_name, image)
            
            # Procesar teclas
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == ord('Q') or key == 27:  # Q o ESC
                print("👋 Saliendo...")
                break
            elif key == ord('r') or key == ord('R'):  # R para reiniciar
                counter = 0
                stage = None
                print("🔄 Contador reiniciado")
                tts_manager.speak("Contador reiniciado")
    
    # Limpieza final
    print(f"\n📊 RESUMEN DE LA SESIÓN:")
    print(f"   🎯 Total de repeticiones: {counter}")
    print(f"   ⏱️ Frames procesados: {frame_count}")
    
    cap.release()
    cv2.destroyAllWindows()
    
    if counter > 0:
        tts_manager.speak(f"Sesión completada. {counter} repeticiones. ¡Buen trabajo!")
    
    print("\n💪 ¡Excelente entrenamiento!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Programa interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()
        print("🏁 Programa finalizado")