# planks.py                # Lógica de planchas
from core.angle_utils import calculate_angle
import mediapipe as mp

pose = mp.solutions.pose

def monitor_plank(landmarks, stage, counter):
    shoulder = [landmarks[pose.PoseLandmark.LEFT_SHOULDER.value].x,
                landmarks[pose.PoseLandmark.LEFT_SHOULDER.value].y]
    hip = [landmarks[pose.PoseLandmark.LEFT_HIP.value].x,
           landmarks[pose.PoseLandmark.LEFT_HIP.value].y]
    ankle = [landmarks[pose.PoseLandmark.LEFT_ANKLE.value].x,
             landmarks[pose.PoseLandmark.LEFT_ANKLE.value].y]

    angle = calculate_angle(shoulder, hip, ankle)

    if 160 <= angle <= 180:
        stage = "buena postura"
    else:
        stage = "mala postura"

    # No se cuenta repeticiones, pero se retorna el estado de la postura
    return angle, stage, counter
