# pushups.py               # Lógica de flexiones
from core.angle_utils import calculate_angle
import mediapipe as mp

pose = mp.solutions.pose

def count_pushup(landmarks, stage, counter):
    shoulder = [landmarks[pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                landmarks[pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    elbow = [landmarks[pose.PoseLandmark.RIGHT_ELBOW.value].x,
             landmarks[pose.PoseLandmark.RIGHT_ELBOW.value].y]
    wrist = [landmarks[pose.PoseLandmark.RIGHT_WRIST.value].x,
             landmarks[pose.PoseLandmark.RIGHT_WRIST.value].y]

    angle = calculate_angle(shoulder, elbow, wrist)

    if angle < 90:
        stage = "abajo"
    if angle > 160 and stage == "abajo":
        stage = "arriba"
        counter += 1

    return angle, stage, counter
