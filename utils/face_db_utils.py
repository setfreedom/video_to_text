import os
import json
import cv2
import numpy as np
from .face_utils import extract_faces, cluster_faces

OUTPUT_DIR = "outputs"
FACE_DIR = os.path.join(OUTPUT_DIR, "faces")
DB_PATH = os.path.join(OUTPUT_DIR, "face_db.json")

def build_face_database(video_path):
    if os.path.exists(DB_PATH):
        print("✅ 已存在人物库，跳过人脸提取")
        return

    os.makedirs(FACE_DIR, exist_ok=True)
    
    # Step 1: 提取（现在返回更多信息）
    encodings, frame_indices, face_boxes = extract_faces(video_path, interval=15)  # 缩短间隔防漏人！
    
    if not encodings:
        print("未检测到任何人脸。")
        return
    
    # Step 2: 聚类
    clusters = cluster_faces(encodings, threshold=0.45)  # 略调低阈值更精细
    
    # Step 3: 重新打开视频，按需读取帧裁剪代表图
    cap = cv2.VideoCapture(video_path)
    face_db = {}
    
    for i, cluster in enumerate(clusters):
        # 从该 cluster 中选择“最佳”人脸：比如 box 面积最大（通常最清晰）
        best_idx = None
        best_area = -1
        for local_idx, global_idx in enumerate(cluster["indices"]):
            frame_idx = frame_indices[global_idx]
            (top, right, bottom, left) = face_boxes[global_idx]
            area = (bottom - top) * (right - left)
            if area > best_area:
                best_area = area
                best_idx = global_idx  # 全局索引
        
        # 读取对应帧并裁剪
        target_frame_idx = frame_indices[best_idx]
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame_idx)
        ret, frame = cap.read()
        if not ret:
            continue
        
        (top, right, bottom, left) = face_boxes[best_idx]
        face_img = frame[top:bottom, left:right]
        path = f"faces/person_{i}.jpg"
        img_path = os.path.join(OUTPUT_DIR, path)
        cv2.imwrite(img_path, face_img)
        
        face_db[str(i)] = {
            "name": f"未知人物_{i}",
            "image": path
        }
    
    cap.release()
    
    # 保存数据库
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(face_db, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 人脸数据库构建完成，共识别 {len(clusters)} 人。")