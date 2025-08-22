import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import threading
import time

# Inicializa TTS
class TTSManager:
    def __init__(self):
        self.engine = None
        self.initialize_tts()

    def initialize_tts(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 160)
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'helena' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"TTS error: {e}")
            self.engine = None

    def speak(self, text):
        if self.engine:
            def _speak():
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except:
                    pass
            threading.Thread(target=_speak, daemon=True).start()
        else:
            print(f"TTS: {text}")

tts_manager = TTSManager()

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def contar_dedos(hand_landmarks):
    dedos = []

    # Pulgar (landmark 4 más a la derecha o izquierda que 3)
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        dedos.append(1)
    else:
        dedos.append(0)

    # Otros 4 dedos
    for tip_id in [8, 12, 16, 20]:
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
            dedos.append(1)
        else:
            dedos.append(0)

    return sum(dedos)

def main():
    print("🖐️ CONTADOR DE MANOS ABIERTAS")
    print("=" * 40)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as hands:

        contador = 0
        mano_abierta_anterior = False
        speak_cooldown = 2.0
        last_speak_time = 0

        window_name = 'Contador de Manos - Presiona Q para salir'
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

        print("🙌 Coloca tu mano frente a la cámara")
        print("Presiona Q para salir")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ No se pudo leer frame")
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            mano_actualmente_abierta = False

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    dedos_extendidos = contar_dedos(hand_landmarks)
                    
                    if dedos_extendidos >= 5:
                        mano_actualmente_abierta = True

                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Contar nueva mano abierta
            if mano_actualmente_abierta and not mano_abierta_anterior:
                contador += 1
                print(f"🖐️ Mano abierta detectada #{contador}")
                current_time = time.time()
                if current_time - last_speak_time > speak_cooldown:
                    tts_manager.speak(f"Mano número {contador}")
                    last_speak_time = current_time

            mano_abierta_anterior = mano_actualmente_abierta

            # Mostrar contador
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (400, 100), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

            cv2.putText(frame, 'CONTADOR DE MANOS ABIERTAS', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f'REPETICIONES: {contador}', (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)

            cv2.imshow(window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q') or key == 27:
                print("👋 Saliendo...")
                break
            elif key == ord('r') or key == ord('R'):
                contador = 0
                mano_abierta_anterior = False
                print("🔄 Contador reiniciado")
                tts_manager.speak("Contador reiniciado")

    cap.release()
    cv2.destroyAllWindows()

    print(f"\n📊 Total de manos abiertas detectadas: {contador}")
    tts_manager.speak(f"Sesión completada. Detectaste {contador} manos abiertas.")

if __name__ == "__main__":
    main()
