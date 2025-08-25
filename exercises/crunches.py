# crunches.py              # Lógica de abdominales
from core.angle_utils import calculate_angle
import mediapipe as mp

pose = mp.solutions.pose

def count_crunch(landmarks, stage, counter):
    shoulder = [landmarks[pose.PoseLandmark.LEFT_SHOULDER.value].x,
                landmarks[pose.PoseLandmark.LEFT_SHOULDER.value].y]
    hip = [landmarks[pose.PoseLandmark.LEFT_HIP.value].x,
           landmarks[pose.PoseLandmark.LEFT_HIP.value].y]
    knee = [landmarks[pose.PoseLandmark.LEFT_KNEE.value].x,
            landmarks[pose.PoseLandmark.LEFT_KNEE.value].y]

    angle = calculate_angle(shoulder, hip, knee)

    if angle < 100:
        stage = "abajo"
    if angle > 140 and stage == "abajo":
        stage = "arriba"
        counter += 1

    return angle, stage, counter
