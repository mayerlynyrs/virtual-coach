
# CONFIGURACIÓN PERSONALIZADA PARA TU SISTEMA
# Generada automáticamente - 2025-08-22 11:43:28

import cv2

def create_camera():
    """Crea una instancia de cámara con la configuración óptima para tu sistema"""
    camera_id = 0
    backend = 700  # DirectShow
    
    cap = cv2.VideoCapture(camera_id, backend)
    
    if cap.isOpened():
        # Configuraciones optimizadas
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        print("✓ Cámara inicializada correctamente")
        return cap
    else:
        print("✗ Error inicializando cámara")
        return None

# Ejemplo de uso:
if __name__ == "__main__":
    cap = create_camera()
    if cap:
        while True:
            ret, frame = cap.read()
            if ret:
                cv2.imshow('Mi Cámara', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        cap.release()
        cv2.destroyAllWindows()
