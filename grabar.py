import cv2

# Intenta abrir la cámara con DirectShow (Windows)
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Verifica si la cámara se abrió correctamente
if not cam.isOpened():
    print("No se pudo abrir la cámara")
    exit()

# Define el códec y el archivo de salida (.mp4 con códec compatible)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('grabacion.mp4', fourcc, 20.0, (640, 480))

print("Grabando... Presiona 'q' para detener.")

while True:
    ret, frame = cam.read()
    if not ret:
        print("No se pudo capturar el video")
        break

    out.write(frame)
    cv2.imshow('Grabando', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera recursos
cam.release()
out.release()
cv2.destroyAllWindows()

print("Grabación finalizada y guardada como grabacion.mp4")
