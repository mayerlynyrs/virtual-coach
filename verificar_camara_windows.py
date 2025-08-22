import cv2
import time
import platform
import subprocess
import sys

def check_windows_camera_permissions():
    """Verifica permisos de cámara en Windows"""
    print("=== VERIFICANDO PERMISOS DE CÁMARA EN WINDOWS ===")
    
    try:
        # Comando PowerShell para verificar permisos de cámara
        ps_command = """
        Get-AppxPackage Microsoft.WindowsCamera | Select-Object Name, InstallLocation
        """
        
        result = subprocess.run(
            ["powershell", "-Command", ps_command], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ Aplicación de cámara de Windows detectada")
        else:
            print("⚠️ Problema con la aplicación de cámara de Windows")
            
    except Exception as e:
        print(f"No se pudo verificar permisos: {e}")

def test_camera_with_all_backends():
    """Prueba todos los backends disponibles de OpenCV"""
    print("\n=== PROBANDO TODOS LOS BACKENDS DE OPENCV ===")
    
    # Backends más comunes en Windows
    backends = {
        cv2.CAP_DSHOW: "DirectShow",
        cv2.CAP_MSMF: "Microsoft Media Foundation", 
        cv2.CAP_V4L2: "Video4Linux2",
        cv2.CAP_FFMPEG: "FFmpeg",
        cv2.CAP_ANY: "Cualquier backend"
    }
    
    successful_backends = []
    
    for camera_id in range(4):  # Probar cámaras 0-3
        print(f"\n--- Probando Cámara {camera_id} ---")
        
        for backend_id, backend_name in backends.items():
            try:
                print(f"  Probando {backend_name}...")
                cap = cv2.VideoCapture(camera_id, backend_id)
                
                if cap.isOpened():
                    # Intentar configurar propiedades
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    # Probar leer frame
                    ret, frame = cap.read()
                    
                    if ret and frame is not None:
                        height, width = frame.shape[:2]
                        print(f"    ✓ Éxito! Resolución: {width}x{height}")
                        
                        # Mostrar frame por 2 segundos
                        cv2.imshow(f'Test: Cámara {camera_id} - {backend_name}', frame)
                        cv2.waitKey(2000)
                        cv2.destroyAllWindows()
                        
                        successful_backends.append({
                            'camera': camera_id,
                            'backend_id': backend_id,
                            'backend_name': backend_name,
                            'resolution': f"{width}x{height}"
                        })
                    else:
                        print(f"    ✗ No se pudo leer frame")
                else:
                    print(f"    ✗ No se pudo abrir")
                
                cap.release()
                
            except Exception as e:
                print(f"    ✗ Error: {e}")
                
            time.sleep(0.5)  # Pausa entre pruebas
    
    return successful_backends

def generate_camera_code(successful_backends):
    """Genera código personalizado basado en las cámaras que funcionan"""
    
    if not successful_backends:
        print("\n❌ NO SE ENCONTRARON CÁMARAS FUNCIONALES")
        return
    
    print(f"\n✅ SE ENCONTRARON {len(successful_backends)} CONFIGURACIONES FUNCIONALES:")
    
    for i, config in enumerate(successful_backends):
        print(f"{i+1}. Cámara {config['camera']} con {config['backend_name']} ({config['resolution']})")
    
    # Usar la primera configuración exitosa
    best_config = successful_backends[0]
    
    print(f"\n📝 CONFIGURACIÓN RECOMENDADA:")
    print(f"   Cámara: {best_config['camera']}")
    print(f"   Backend: {best_config['backend_name']} ({best_config['backend_id']})")
    print(f"   Resolución: {best_config['resolution']}")
    
    # Generar código personalizado
    custom_code = f"""
# CONFIGURACIÓN PERSONALIZADA PARA TU SISTEMA
# Generada automáticamente - {time.strftime('%Y-%m-%d %H:%M:%S')}

import cv2

def create_camera():
    \"\"\"Crea una instancia de cámara con la configuración óptima para tu sistema\"\"\"
    camera_id = {best_config['camera']}
    backend = {best_config['backend_id']}  # {best_config['backend_name']}
    
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
"""
    
    # Guardar código personalizado
    with open('mi_camara_personalizada.py', 'w', encoding='utf-8') as f:
        f.write(custom_code)
    
    print("\n💾 Código personalizado guardado en 'mi_camara_personalizada.py'")
    
    return best_config

def check_camera_processes():
    """Verifica procesos que podrían estar usando la cámara"""
    print("\n=== VERIFICANDO PROCESOS QUE USAN LA CÁMARA ===")
    
    suspicious_processes = [
        'Teams.exe', 'Zoom.exe', 'chrome.exe', 'firefox.exe', 
        'obs64.exe', 'obs32.exe', 'skype.exe', 'discord.exe',
        'ApplicationFrameHost.exe'  # App de Cámara de Windows
    ]
    
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        running_processes = result.stdout.lower()
        
        found_processes = []
        for process in suspicious_processes:
            if process.lower() in running_processes:
                found_processes.append(process)
        
        if found_processes:
            print("⚠️ Procesos que podrían estar usando la cámara:")
            for process in found_processes:
                print(f"   - {process}")
            print("\n💡 Considera cerrar estas aplicaciones antes de usar la cámara")
        else:
            print("✓ No se encontraron procesos sospechosos")
            
    except Exception as e:
        print(f"No se pudo verificar procesos: {e}")

def main():
    print("VERIFICADOR DE CÁMARA PARA WINDOWS")
    print("=" * 50)
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"OpenCV: {cv2.__version__}")
    print(f"Python: {sys.version.split()[0]}")
    
    # Verificaciones
    check_windows_camera_permissions()
    check_camera_processes()
    
    print("\n🔍 Iniciando pruebas exhaustivas de cámara...")
    print("Esto puede tardar un momento...")
    
    successful_backends = test_camera_with_all_backends()
    
    if successful_backends:
        config = generate_camera_code(successful_backends)
        
        print("\n" + "=" * 50)
        print("🎉 ¡CÁMARA ENCONTRADA!")
        print("\nPara usar en tu aplicación principal, modifica la línea:")
        print("   cap = cv2.VideoCapture(0)")
        print("Por:")
        print(f"   cap = cv2.VideoCapture({config['camera']}, {config['backend_id']})")
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Ejecuta 'python mi_camara_personalizada.py' para probar")
        print("2. Si funciona, aplica la configuración a tu aplicación principal")
        print("3. ¡Disfruta tu contador de sentadillas!")
        
    else:
        print("\n" + "=" * 50)
        print("❌ NO SE PUDO ACCEDER A NINGUNA CÁMARA")
        print("\n🔧 SOLUCIONES ADICIONALES:")
        print("1. Reinicia tu computadora")
        print("2. Actualiza drivers de cámara en Administrador de dispositivos")
        print("3. Ejecuta Windows Update")
        print("4. Verifica antivirus (puede estar bloqueando acceso)")
        print("5. Prueba con una cámara USB externa")
        
        print("\n🏥 DIAGNÓSTICO AVANZADO:")
        print("- Abre 'Administrador de dispositivos'")
        print("- Busca 'Cámaras' o 'Dispositivos de imagen'")
        print("- Si hay signos de exclamación (⚠️), hay problemas de driver")
        print("- Click derecho → 'Desinstalar' → Reiniciar → Windows reinstalará")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()
