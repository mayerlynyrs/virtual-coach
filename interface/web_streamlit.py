import streamlit as st
import subprocess
import sys
import os

EXERCISES = {
    "Sentadillas": "squat",
    "Flexiones": "pushup",
    "Zancadas": "lunge",
    "Planchas": "plank",
    "Abdominales": "crunch"
}

st.set_page_config(page_title="Virtual Coach Web", layout="centered")

st.title("🤖 Virtual Coach")
st.markdown("Selecciona un ejercicio para comenzar:")

selected = st.selectbox("Ejercicio", list(EXERCISES.keys()))

if st.button("Iniciar"):
    exercise_type = EXERCISES[selected]

    with open("config.py", "w") as f:
        f.write(f'VIDEO_WIDTH = 640\nVIDEO_HEIGHT = 480\nEXERCISE_TYPE = "{exercise_type}"\n')

    python_exe = sys.executable
    subprocess.Popen([python_exe, "main.py"])
    st.success(f"Iniciando ejercicio: {selected}...")

st.markdown("---")
st.caption("© 2025 Virtual Coach - OpenAI Inspired")
