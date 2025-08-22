import sys
import cv2
import mediapipe as mp
import pyttsx3

def test_camera():
    print("=== DIAGNÓSTICO DE CÁMARA ===")
    camera_found = False
    
    for i in range(5):  # Probar índices 0-4
        try:
            print(f"Probando cámara índice {i}...")
            cap = cv2.VideoCapture(i)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✓ Cámara {i} funciona - Resolución: {frame.shape}")
                    camera_found = True
                    
                    # Mostrar frame de prueba
                    cv2.imshow(f'Test Camera {i}', frame)
                    cv2.waitKey(2000)  # Mostrar por 2 segundos
                    cv2.destroyAllWindows()
                else:
                    print(f"✗ Cámara {i} no puede leer frames")
                cap.release()
            else:
                print(f"✗ No se puede abrir cámara {i}")
                if cap:
                    cap.release()
                    
        except Exception as e:
            print(f"✗ Error con cámara {i}: {e}")
    
    if not camera_found:
        print("\n❌ NO SE ENCONTRÓ NINGUNA CÁMARA FUNCIONAL")
        print("Posibles soluciones:")
        print("- Verifica que la cámara esté conectada")
        print("- Cierra otras apps que usen la cámara (Zoom, Teams, etc.)")
        print("- Reinicia el sistema")
        print("- Verifica permisos de cámara en tu OS")
    else:
        print(f"\n✓ Al menos una cámara funciona correctamente")
    
    return camera_found

def test_opencv():
    print("\n=== DIAGNÓSTICO DE OPENCV ===")
    try:
        print(f"OpenCV versión: {cv2.__version__}")
        print("✓ OpenCV instalado correctamente")
        return True
    except Exception as e:
        print(f"✗ Error con OpenCV: {e}")
        return False

def test_mediapipe():
    print("\n=== DIAGNÓSTICO DE MEDIAPIPE ===")
    try:
        mp_pose = mp.solutions.pose
        print(f"MediaPipe importado correctamente")
        
        # Probar inicialización
        with mp_pose.Pose() as pose:
            print("✓ MediaPipe Pose inicializado correctamente")
        return True
    except Exception as e:
        print(f"✗ Error con MediaPipe: {e}")
        return False

def test_tts():
    print("\n=== DIAGNÓSTICO DE TTS ===")
    try:
        engine = pyttsx3.init()
        
        # Listar voces disponibles
        voices = engine.getProperty('voices')
        print(f"Voces disponibles: {len(voices)}")
        
        for i, voice in enumerate(voices[:3]):  # Mostrar solo las primeras 3
            print(f"  {i}: {voice.name} - {voice.id}")
        
        # Probar TTS
        print("Probando TTS...")
        engine.say("Prueba de texto a voz")
        engine.runAndWait()
        print("✓ TTS funciona correctamente")
        return True
        
    except Exception as e:
        print(f"✗ Error con TTS: {e}")
        print("Nota: TTS puede no funcionar pero el programa principal sí")
        return False

def test_window_display():
    print("\n=== DIAGNÓSTICO DE VENTANAS ===")
    try:
        # Crear ventana de prueba
        test_image = cv2.imread('test.jpg') if False else None
        if test_image is None:
            # Crear imagen de prueba
            import numpy as np
            test_image = np.zeros((300, 400, 3), dtype=np.uint8)
            cv2.putText(test_image, 'VENTANA DE PRUEBA', (50, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        cv2.imshow('Test Window', test_image)
        print("✓ Ventana creada. Presiona cualquier tecla para continuar...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print("✓ Sistema de ventanas funciona correctamente")
        return True
        
    except Exception as e:
        print(f"✗ Error mostrando ventanas: {e}")
        print("Posibles causas:")
        print("- Sistema sin interfaz gráfica (servidor/SSH)")
        print("- Problemas con el sistema de ventanas")
        return False

def main():
    print("DIAGNÓSTICO COMPLETO DEL SISTEMA")
    print("=" * 50)
    
    results = []
    results.append(("OpenCV", test_opencv()))
    results.append(("MediaPipe", test_mediapipe()))
    results.append(("Cámara", test_camera()))
    results.append(("TTS", test_tts()))
    results.append(("Ventanas", test_window_display()))
    
    print("\n" + "=" * 50)
    print("RESUMEN:")
    
    all_good = True
    for component, status in results:
        status_str = "✓ OK" if status else "✗ ERROR"
        print(f"{component:12}: {status_str}")
        if not status:
            all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 TODOS LOS COMPONENTES FUNCIONAN CORRECTAMENTE")
        print("Tu aplicación debería funcionar sin problemas.")
    else:
        print("⚠️  HAY PROBLEMAS CON ALGUNOS COMPONENTES")
        print("Revisa los errores específicos arriba.")
    
    print(f"\nPython: {sys.version}")
    print(f"Sistema: {sys.platform}")

if __name__ == "__main__":
    main()
