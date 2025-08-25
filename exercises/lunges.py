# lunges.py                # Lógica de zancadas
from core.angle_utils import calculate_angle
import mediapipe as mp

pose = mp.solutions.pose

def count_lunge(landmarks, stage, counter):
    hip = [landmarks[pose.PoseLandmark.LEFT_HIP.value].x,
           landmarks[pose.PoseLandmark.LEFT_HIP.value].y]
    knee = [landmarks[pose.PoseLandmark.LEFT_KNEE.value].x,
            landmarks[pose.PoseLandmark.LEFT_KNEE.value].y]
    ankle = [landmarks[pose.PoseLandmark.LEFT_ANKLE.value].x,
             landmarks[pose.PoseLandmark.LEFT_ANKLE.value].y]

    angle = calculate_angle(hip, knee, ankle)

    if angle < 90:
        stage = "abajo"
    if angle > 160 and stage == "abajo":
        stage = "arriba"
        counter += 1

    return angle, stage, counter
