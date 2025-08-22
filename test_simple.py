import cv2
import time

print("Probando cámara simple...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Forzar DirectShow

if cap.isOpened():
    for i in range(10):  # Intentar 10 veces
        ret, frame = cap.read()
        print(f"Intento {i+1}: {ret}, Frame shape: {frame.shape if ret else 'None'}")
        time.sleep(0.5)
    cap.release()
else:
    print("No se pudo abrir la cámara")