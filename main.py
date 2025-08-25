from core.pose_estimation import get_keypoints, setup_mediapipe
from core.rep_counter import process_exercise
from core.feedback_audio import give_feedback
from config import VIDEO_WIDTH, VIDEO_HEIGHT, EXERCISE_TYPE
import cv2

# Captura de cámara
# cap = cv2.VideoCapture(0) # Para macOS/Linux
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Para Windows
cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)

counter = 0
stage = None

with setup_mediapipe() as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        landmarks, image = get_keypoints(frame, pose)

        if landmarks:
            angle, stage, counter = process_exercise(EXERCISE_TYPE, landmarks, stage, counter)
            give_feedback(angle, stage, counter, image)
        else:
            cv2.putText(image, "Persona no detectada", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Virtual Coach", image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
