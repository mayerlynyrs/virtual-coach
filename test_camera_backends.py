import cv2

backends = {
    "ANY": cv2.CAP_ANY,
    "VFW": cv2.CAP_VFW,
    "DSHOW": cv2.CAP_DSHOW,
    "MSMF": cv2.CAP_MSMF,
    "FFMPEG": cv2.CAP_FFMPEG,
}

print("🔍 Probando backends disponibles...\n")

for name, backend in backends.items():
    print(f"🔧 Intentando con backend: {name}")
    cap = cv2.VideoCapture(0, backend)
    
    if not cap.isOpened():
        print(f"  ❌ No se pudo abrir la camara con {name}")
        continue

    ret, frame = cap.read()
    if not ret:
        print(f"  ⚠️  Camara abierta pero no entrega imagen con {name}")
        cap.release()
        continue

    print(f"  ✅ Funciona correctamente con backend: {name}")

    # Mostrar frame por 3 segundos
    cv2.imshow(f'Camara ({name})', frame)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()
    cap.release()
    break
else:
    print("\n❌ No se encontró ningún backend funcional. La camara no entrega imagen.")
