import cv2
import face_recognition
import numpy as np
from sklearn.cluster import DBSCAN

# 返回: (encodings, frame_indices, face_locations_per_frame)
def extract_faces(video_path, interval=30):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if fps <= 0:
        raise ValueError("无法读取视频帧率")
    
    frame_interval = int(fps * interval)
    encodings = []
    frame_indices = []      # 记录每张人脸来自哪一帧
    face_boxes = []         # 记录每张人脸的 bounding box

    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_interval == 0:
            # 可选：缩放帧以加速（如 width=640）
            scale = 640 / max(frame.shape[1], 1)
            if scale < 1:
                small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
            else:
                small_frame = frame

            # 检测人脸（使用 HOG，但 on smaller image）
            boxes = face_recognition.face_locations(small_frame, model="hog")
            if boxes:
                # 恢复原始坐标（如果缩放过）
                orig_boxes = [(int(top/scale), int(right/scale), int(bottom/scale), int(left/scale)) 
                              for (top, right, bottom, left) in boxes]
                encs = face_recognition.face_encodings(frame, known_face_locations=orig_boxes)
                for enc, box in zip(encs, orig_boxes):
                    encodings.append(enc)
                    frame_indices.append(frame_idx)
                    face_boxes.append(box)
        frame_idx += 1

    cap.release()
    return encodings, frame_indices, face_boxes



def cluster_faces(encodings, threshold=0.5):
    if not encodings:
        return []
    
    # 转为 numpy array
    X = np.array(encodings)
    
    # DBSCAN: eps ≈ threshold, min_samples=2 防止噪声点成簇
    clustering = DBSCAN(eps=threshold, min_samples=2, metric="euclidean").fit(X)
    labels = clustering.labels_
    
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    clusters = []
    
    for label in set(labels):
        if label == -1:  # 噪声点（未归类人脸）
            continue
        members = X[labels == label]
        center = members.mean(axis=0)
        clusters.append({
            "center": center,
            "members": members.tolist(),
            "indices": np.where(labels == label)[0].tolist()  # 成员在原列表中的索引
        })
    
    # 处理噪声点：每个单独成簇（可选）
    noise_indices = np.where(labels == -1)[0]
    for idx in noise_indices:
        clusters.append({
            "center": X[idx],
            "members": [X[idx].tolist()],
            "indices": [idx]
        })
    
    return clusters