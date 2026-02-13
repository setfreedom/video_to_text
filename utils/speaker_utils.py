import json
import cv2
import face_recognition
import numpy as np
from pathlib import Path

FACE_DB_PATH = "outputs/face_db.json"


def load_face_db():
    with open(FACE_DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_face_encodings():
    db = load_face_db()

    encodings = []
    names = []

    for pid, info in db.items():
        img_path = Path("outputs") / info["image"]
        img = face_recognition.load_image_file(str(img_path))
        enc = face_recognition.face_encodings(img)

        if enc:
            encodings.append(enc[0])
            names.append(info["name"])

    return encodings, names


def identify_speaker(frame, known_encodings, known_names, threshold=0.5):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb)
    encs = face_recognition.face_encodings(rgb, boxes)

    if not encs:
        return "未知"

    best_name = "未知"
    best_dist = 999

    for enc in encs:
        dists = face_recognition.face_distance(known_encodings, enc)
        idx = np.argmin(dists)
        if dists[idx] < best_dist and dists[idx] < threshold:
            best_dist = dists[idx]
            best_name = known_names[idx]

    return best_name


def assign_speakers(video_path, dialogues):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    known_encodings, known_names = load_face_encodings()

    for dlg in dialogues:
        t = (dlg.start_time + dlg.end_time) / 2
        frame_idx = int(t * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()

        if ret:
            name = identify_speaker(frame, known_encodings, known_names)
            dlg.speaker = name

    cap.release()
    return dialogues
