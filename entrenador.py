import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import time

# Inicializa MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Inicializa TTS (voz)
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Velocidad de voz
# Configura voz en español (puede variar según el sistema)
voices = engine.getProperty('voices')
for voice in voices:
    if "spanish" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

# Función para calcular ángulo entre tres puntos
def calculate_angle(a, b, c):
    a = np.array(a)  # Primer punto
    b = np.array(b)  # Punto medio
    c = np.array(c)  # Tercer punto
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# Configuración del ejercicio
ejercicio = "sentadillas"
objetivo_reps = 20
reps = 0
estado = "arriba"  # Para contar reps (arriba/abajo)
ultimo_feedback = time.time()  # Para no repetir feedback muy rápido

# Captura de video (cámara 0 es la default)
cap = cv2.VideoCapture(0)

print("Colócate frente a la cámara. Presiona 'q' para salir.")
engine.say("Bienvenido. Vamos a hacer 20 sentadillas. Comienza cuando estés listo.")
engine.runAndWait()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: No se puede acceder a la cámara.")
        break
    
    # Convierte a RGB para MediaPipe
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    
    # Procesa la pose
    results = pose.process(image)
    
    # Dibuja landmarks si se detecta pose
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # Extrae landmarks clave (para sentadillas: hombros, caderas, rodillas, tobillos)
        landmarks = results.pose_landmarks.landmark
        hombro_izq = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        cadera_izq = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        rodilla_izq = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        tobillo_izq = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        
        # Calcula ángulos
        angulo_rodilla = calculate_angle(cadera_izq, rodilla_izq, tobillo_izq)
        angulo_espalda = calculate_angle(hombro_izq, cadera_izq, rodilla_izq)  # Aproximación para espalda
        
        # Lógica de conteo de reps (basado en posición de cadera)
        altura_cadera = cadera_izq[1]  # Y-coordinate (menor = más arriba)
        if estado == "arriba" and altura_cadera > 0.6:  # Bajando
            estado = "abajo"
        elif estado == "abajo" and altura_cadera < 0.5:  # Subiendo
            reps += 1
            estado = "arriba"
            print(f"Repetición: {reps}/{objetivo_reps}")
            if reps >= objetivo_reps:
                engine.say("¡Felicidades! Has completado las sentadillas.")
                engine.runAndWait()
                break
        
        # Verifica forma y da feedback (cada 2 segundos max)
        ahora = time.time()
        if ahora - ultimo_feedback > 2:
            if angulo_rodilla < 90:
                engine.say("Baja más las rodillas.")
                engine.runAndWait()
                ultimo_feedback = ahora
            elif rodilla_izq[0] - tobillo_izq[0] > 0.1:
                engine.say("No dejes que las rodillas pasen los pies.")
                engine.runAndWait()
                ultimo_feedback = ahora
            elif angulo_espalda < 150:
                engine.say("Mantén la espalda recta.")
                engine.runAndWait()
                ultimo_feedback = ahora
    
    # Muestra el video con overlays
    cv2.putText(image, f"Reps: {reps}/{objetivo_reps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('Entrenador Personal', image)
    
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()