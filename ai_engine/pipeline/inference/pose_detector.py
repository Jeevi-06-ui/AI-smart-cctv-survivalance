import cv2
import numpy as np
import time
import math
from typing import List, Dict, Tuple, Any

try:
    from ultralytics import YOLO
except ImportError:
    print("[ERROR] ultralytics package not found!")
    YOLO = None

class YOLOPoseDetector:
    """
    Real Ultralytics YOLO Pose Estimation & Fall Detection Engine.
    Detects 17 human keypoints, tracks people, and calculates fall events based on skeleton geometry.
    """
    def __init__(self, model_path: str = "yolov8n-pose.pt", confidence_threshold: float = 0.5):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.fps = 0.0
        
        if YOLO is not None:
            print(f"[Pose Engine] Loading model {model_path}...")
            self.model = YOLO(model_path)
            print(f"[Pose Engine] Initialized Real YOLO Pose & Fall Detector")
        else:
            self.model = None
            print("[Pose Engine] WARNING: Running without YOLO.")

    def detect_fall(self, keypoints, bbox) -> Tuple[bool, float]:
        """
        Determines if a person has fallen based on bounding box ratio and torso angle.
        Returns (is_fallen, confidence)
        """
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        
        if height == 0 or width == 0:
            return False, 0.0

        ratio = width / float(height)
        
        # Keypoint indices: 5=L_Shoulder, 6=R_Shoulder, 11=L_Hip, 12=R_Hip
        # Ensure keypoints are valid (confidence/visibility)
        try:
            # Flatten keypoints if they are in tensor format
            kpts = keypoints.cpu().numpy() if hasattr(keypoints, 'cpu') else keypoints
            
            l_shoulder = kpts[5]
            r_shoulder = kpts[6]
            l_hip = kpts[11]
            r_hip = kpts[12]
            
            # If coordinates are 0,0 they weren't detected
            if np.all(l_shoulder == 0) or np.all(l_hip == 0):
                # Fallback to bounding box ratio if skeleton is occluded
                is_fallen = ratio > 1.2
                return is_fallen, min(0.85, ratio / 2.0) if is_fallen else 0.0

            # Calculate torso center points
            shoulder_mid_x = (l_shoulder[0] + r_shoulder[0]) / 2.0
            shoulder_mid_y = (l_shoulder[1] + r_shoulder[1]) / 2.0
            hip_mid_x = (l_hip[0] + r_hip[0]) / 2.0
            hip_mid_y = (l_hip[1] + r_hip[1]) / 2.0
            
            # Calculate angle of torso relative to vertical
            dx = hip_mid_x - shoulder_mid_x
            dy = hip_mid_y - shoulder_mid_y
            
            # Angle in degrees (0 is perfectly vertical, 90 is horizontal)
            angle = math.degrees(math.atan2(abs(dx), abs(dy)))
            
            # Fall condition: Torso is highly angled (>60 deg) OR bbox is wider than tall
            is_fallen = angle > 60 or ratio > 1.2
            conf = min(0.99, (angle / 90.0) if angle > 60 else (ratio / 2.0))
            
            return is_fallen, conf
            
        except Exception as e:
            # Fallback to pure bounding box logic if keypoint extraction fails
            is_fallen = ratio > 1.2
            return is_fallen, 0.75 if is_fallen else 0.0

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict[str, Any]], Dict[str, Any]]:
        start_time = time.time()
        annotated_frame = frame.copy()
        detections = []
        fall_events = 0
        
        if self.model is None:
            return annotated_frame, detections, {"error": "Model not loaded"}

        # Run YOLO real-time pose tracking
        results = self.model.track(frame, persist=True, conf=self.confidence_threshold, verbose=False)
        
        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            confidences = results[0].boxes.conf.cpu().numpy()
            
            # Extract keypoints if available
            keypoints_data = results[0].keypoints.xy if results[0].keypoints is not None else [None]*len(boxes)
            
            for box, track_id, conf, kpts in zip(boxes, track_ids, confidences, keypoints_data):
                x1, y1, x2, y2 = map(int, box)
                
                # Check for fall
                is_fallen, fall_conf = self.detect_fall(kpts, box)
                if is_fallen:
                    fall_events += 1

                det_info = {
                    "track_id": track_id,
                    "label": "person",
                    "confidence": float(conf),
                    "bbox": [x1, y1, x2, y2],
                    "is_fallen": is_fallen,
                    "fall_confidence": fall_conf
                }
                detections.append(det_info)
                
                # Draw Box (Red if fallen, Cyan if standing)
                box_color = (0, 0, 255) if is_fallen else (255, 240, 0)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), box_color, 2)
                
                # Draw Skeleton
                if kpts is not None:
                    kpts_np = kpts.cpu().numpy() if hasattr(kpts, 'cpu') else kpts
                    for pt in kpts_np:
                        px, py = int(pt[0]), int(pt[1])
                        if px > 0 and py > 0:
                            cv2.circle(annotated_frame, (px, py), 3, (0, 255, 0), -1)
                
                # Draw Label & Fall Alert
                status_text = f"FALLEN {int(fall_conf*100)}%" if is_fallen else "STANDING"
                label_text = f"ID:{track_id} {status_text}"
                
                (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(annotated_frame, (x1, y1 - 20), (x1 + tw + 6, y1), box_color, -1)
                
                text_color = (255, 255, 255) if is_fallen else (0, 0, 0)
                cv2.putText(annotated_frame, label_text, (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)
                
                # Huge flashing alert if someone falls
                if is_fallen:
                    cv2.putText(annotated_frame, "CRITICAL: FALL DETECTED!", (x1, max(30, y1 - 30)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

        exec_time = time.time() - start_time
        self.fps = round(1.0 / max(exec_time, 0.001), 1)
        
        hud_text = f"YOLOv8 Pose Engine | FPS: {self.fps} | Active Persons: {len(detections)}"
        cv2.putText(annotated_frame, hud_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        return annotated_frame, detections, {"fps": self.fps, "falls": fall_events}
