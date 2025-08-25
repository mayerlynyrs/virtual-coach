# squats.py                # Lógica de sentadillas

from core.angle_utils import calculate_angle
import mediapipe as mp

pose = mp.solutions.pose

def count_squat(landmarks, stage, counter):
    hip = [landmarks[pose.PoseLandmark.RIGHT_HIP.value].x,
           landmarks[pose.PoseLandmark.RIGHT_HIP.value].y]
    knee = [landmarks[pose.PoseLandmark.RIGHT_KNEE.value].x,
            landmarks[pose.PoseLandmark.RIGHT_KNEE.value].y]
    ankle = [landmarks[pose.PoseLandmark.RIGHT_ANKLE.value].x,
             landmarks[pose.PoseLandmark.RIGHT_ANKLE.value].y]

    angle = calculate_angle(hip, knee, ankle)

    if angle < 90:
        stage = "abajo"
    if angle > 150 and stage == "abajo":
        stage = "arriba"
        counter += 1

    return angle, stage, counter
