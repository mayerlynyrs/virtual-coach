from exercises.squats import count_squat
from exercises.pushups import count_pushup
from exercises.lunges import count_lunge
from exercises.planks import monitor_plank
from exercises.crunches import count_crunch

def process_exercise(exercise_type, landmarks, stage, counter):
    if exercise_type == "squat":
        return count_squat(landmarks, stage, counter)
    elif exercise_type == "pushup":
        return count_pushup(landmarks, stage, counter)
    elif exercise_type == "lunge":
        return count_lunge(landmarks, stage, counter)
    elif exercise_type == "plank":
        return monitor_plank(landmarks, stage, counter)
    elif exercise_type == "crunch":
        return count_crunch(landmarks, stage, counter)
    else:
        return None, stage, counter
