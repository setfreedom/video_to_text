import cv2
import face_recognition
import numpy as np


def extract_faces(video_path, interval=30):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval)

    encodings = []
    images = []

    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if idx % frame_interval == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb)
            encs = face_recognition.face_encodings(rgb, boxes)

            for e, (t, r, b, l) in zip(encs, boxes):
                face_img = frame[t:b, l:r]
                encodings.append(e)
                images.append(face_img)

        idx += 1

    cap.release()
    return encodings, images


def cluster_faces(encodings, threshold=0.5):
    clusters = []

    for enc in encodings:
        matched = False
        for c in clusters:
            dist = np.linalg.norm(c["center"] - enc)
            if dist < threshold:
                c["members"].append(enc)
                c["center"] = np.mean(c["members"], axis=0)
                matched = True
                break

        if not matched:
            clusters.append({"center": enc, "members": [enc]})

    return clusters
