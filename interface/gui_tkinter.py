import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

def run_main_with_exercise(exercise_type):
    with open("config.py", "w") as f:
        f.write(f'VIDEO_WIDTH = 640\nVIDEO_HEIGHT = 480\nEXERCISE_TYPE = "{exercise_type}"\n')

    python_exe = sys.executable
    subprocess.Popen([python_exe, "main.py"])

def start_ui():
    root = tk.Tk()
    root.title("Virtual Coach - Selecciona un ejercicio")

    tk.Label(root, text="Selecciona el ejercicio:", font=("Arial", 14)).pack(pady=10)

    exercises = ["squat", "pushup", "lunge", "plank", "crunch"]

    for ex in exercises:
        tk.Button(root, text=ex.capitalize(),
                  command=lambda e=ex: run_main_with_exercise(e),
                  width=20, height=2).pack(pady=5)

    tk.Button(root, text="Salir", command=root.destroy, bg="red", fg="white").pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    start_ui()
