import os
import json
import cv2
from utils.face_utils import extract_faces, cluster_faces

OUTPUT_DIR = "outputs"
FACE_DIR = os.path.join(OUTPUT_DIR, "faces")
DB_PATH = os.path.join(OUTPUT_DIR, "face_db.json")


def build_face_database(video_path):
    if os.path.exists(DB_PATH):
        print("✅ 已存在人物库，跳过人脸提取")
        return

    os.makedirs(FACE_DIR, exist_ok=True)

    encodings, images = extract_faces(video_path)
    clusters = cluster_faces(encodings)

    db = {}

    for i, cluster in enumerate(clusters):
        img = images[i]
        path = f"faces/person_{i}.jpg"
        full_path = os.path.join(OUTPUT_DIR, path)

        cv2.imwrite(full_path, img)

        db[str(i)] = {
            "name": f"未知人物_{i}",
            "image": path
        }

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("✅ 人物数据库生成完成:", DB_PATH)
