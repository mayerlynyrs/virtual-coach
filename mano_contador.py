import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pyttsx3

# Inicializar TTS
engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Configurar Chrome para permitir cámara
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Auto-acepta cámara
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--start-maximized")

# Abrir archivo local
driver = webdriver.Chrome(options=chrome_options)
# driver.get("file:///C:\\Users\\sopor\\prruebaa\\contador.html")
# driver.get("file:///C:/Users/sopor/prruebaa/contador.html")
# driver.get(r"file:///C:\Users\sopor\prruebaa\contador.html")
driver.get("http://localhost:8000/contador.html")



# Espera que cargue
time.sleep(5)

print("🖐️ Esperando manos abiertas...")

last_value = "0"

try:
    while True:
        try:
            counter_element = driver.find_element(By.ID, "counter")
            current_value = counter_element.text.strip()

            if current_value != last_value and current_value.isdigit():
                print(f"🖐️ Mano número {current_value}")
                speak(f"Mano número {current_value}")
                last_value = current_value

            time.sleep(0.5)
        except Exception as e:
            print("❌ Error leyendo contador:", e)
            time.sleep(1)

except KeyboardInterrupt:
    print("🛑 Finalizado por el usuario")
    driver.quit()
