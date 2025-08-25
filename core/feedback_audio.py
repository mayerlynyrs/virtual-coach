import pyttsx3
import cv2

engine = pyttsx3.init()
engine.setProperty('rate', 160)
last_spoken = -1

def give_feedback(angle, stage, counter, image):
    global last_spoken
    cv2.putText(image, f'Ángulo: {int(angle)}', (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(image, f'Reps: {counter}', (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(image, f'Etapa: {stage}', (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    if counter > last_spoken and counter % 5 == 0:
        engine.say(f"{counter} repeticiones completadas")
        engine.runAndWait()
        last_spoken = counter
