import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import math

# Inicializar TTS
engine = pyttsx3.init()
engine.setProperty('rate', 160)

# Inicializar MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Función para calcular el ángulo entre tres puntos
def calculate_angle(a, b, c):
    a = np.array(a)  # Cadera
    b = np.array(b)  # Rodilla
    c = np.array(c)  # Tobillo

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

# Inicializar variables
counter = 0
stage = None  # "arriba" o "abajo"

# Hablar
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Captura de cámara
cap = cv2.VideoCapture(0)

with mp_pose.Pose(min_detection_confidence=0.5,
                  min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Recolor a RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Hacer detección
        results = pose.process(image)

        # Volver a BGR para OpenCV
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark

            # Puntos clave: Cadera, rodilla, tobillo derechos
            hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                   landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                    landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

            angle = calculate_angle(hip, knee, ankle)

            # Mostrar ángulo en pantalla
            cv2.putText(image, f'Angulo: {int(angle)}',
                        (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Lógica de sentadillas
            if angle < 90:
                stage = "abajo"
            if angle > 150 and stage == "abajo":
                stage = "arriba"
                counter += 1
                print(f"Repetición: {counter}")
                speak(f"Repetición {counter}")

        except Exception as e:
            print("Error:", e)

        # Mostrar contador
        cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)
        cv2.putText(image, 'Reps', (15, 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv2.putText(image, str(counter),
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)

        # Mostrar resultado
        cv2.imshow('Entrenamiento Inteligente - Sentadillas', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
