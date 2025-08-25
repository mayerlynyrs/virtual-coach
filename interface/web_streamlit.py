# interface/web_streamlit.py

import sys
import os

# Añadir la raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import cv2
import numpy as np

from core.pose_estimation import get_keypoints, setup_mediapipe
from core.rep_counter import process_exercise
from core.feedback_audio import give_feedback

EXERCISES = {
    "Sentadillas": "squat",
    "Flexiones": "pushup",
    "Zancadas": "lunge",
    "Planchas": "plank",
    "Abdominales": "crunch"
}

st.set_page_config(page_title="Virtual Coach Web", layout="centered")

st.title("🤖 Virtual Coach en Streamlit")
selected = st.selectbox("Selecciona un ejercicio", list(EXERCISES.keys()))
exercise_type = EXERCISES[selected]

st.markdown("Haz clic en **Iniciar** para comenzar el entrenamiento:")

# Estados globales
if "counter" not in st.session_state:
    st.session_state.counter = 0
if "stage" not in st.session_state:
    st.session_state.stage = None


class PoseEstimatorTransformer(VideoTransformerBase):
    def __init__(self):
        self.pose = setup_mediapipe()
        self.pose.__enter__()

    def transform(self, frame: av.VideoFrame) -> np.ndarray:
        img = frame.to_ndarray(format="bgr24")
        landmarks, image = get_keypoints(img, self.pose)

        if landmarks:
            angle, st.session_state.stage, st.session_state.counter = process_exercise(
                exercise_type, landmarks, st.session_state.stage, st.session_state.counter
            )
            give_feedback(angle, st.session_state.stage, st.session_state.counter, image)
        else:
            cv2.putText(image, "Persona no detectada", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return image

# Iniciar cámara
webrtc_streamer(
    key="virtual-coach",
    video_transformer_factory=PoseEstimatorTransformer,
    media_stream_constraints={"video": True, "audio": False},
    async_transform=True
)

# Mostrar feedback de texto
st.markdown("### 📊 Feedback")
st.write(f"**Repeticiones**: {st.session_state.counter}")
st.write(f"**Estado actual**: {st.session_state.stage or 'Esperando...'}")

st.markdown("---")
st.caption("© 2025 Virtual Coach - OpenAI Inspired")
