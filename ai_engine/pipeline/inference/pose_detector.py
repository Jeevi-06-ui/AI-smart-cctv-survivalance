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

    def detect_fall(self, keypoints_xy, keypoints_conf, bbox) -> Tuple[bool, float]:
        """
        Determines if a person has fallen using scale-invariant joint geometry and visibility scores.
        Returns (is_fallen, confidence)
        """
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        
        if height == 0 or width == 0:
            return False, 0.0

        # Lying flat on the floor is extremely horizontal (width is much larger than height)
        # We increase this fallback ratio to 1.6 to prevent any false positives when close to webcam.
        aspect_ratio = width / float(height)
        
        try:
            if keypoints_xy is None or keypoints_conf is None:
                is_fallen = aspect_ratio > 1.6
                return is_fallen, 0.75 if is_fallen else 0.0

            kpts_xy = keypoints_xy.cpu().numpy() if hasattr(keypoints_xy, 'cpu') else keypoints_xy
            kpts_conf = keypoints_conf.cpu().numpy() if hasattr(keypoints_conf, 'cpu') else keypoints_conf
            
            l_shoulder = kpts_xy[5]
            r_shoulder = kpts_xy[6]
            l_hip = kpts_xy[11]
            r_hip = kpts_xy[12]
            
            # Verify if shoulders and hips are visible in the frame with high confidence (>0.45)
            shoulders_visible = kpts_conf[5] > 0.45 and kpts_conf[6] > 0.45
            hips_visible = kpts_conf[11] > 0.45 and kpts_conf[12] > 0.45
            
            # If coordinates are 0,0 or the keypoints are occluded/not-visible (conf < 0.45)
            if not (shoulders_visible and hips_visible) or np.all(l_shoulder == 0) or np.all(l_hip == 0):
                # Fallback to aspect ratio (lying flat is usually > 1.6 ratio)
                is_fallen = aspect_ratio > 1.6
                return is_fallen, min(0.85, aspect_ratio / 2.0) if is_fallen else 0.0

            # Calculate torso center coordinates
            shoulder_mid_x = (l_shoulder[0] + r_shoulder[0]) / 2.0
            shoulder_mid_y = (l_shoulder[1] + r_shoulder[1]) / 2.0
            hip_mid_x = (l_hip[0] + r_hip[0]) / 2.0
            hip_mid_y = (l_hip[1] + r_hip[1]) / 2.0
            
            # Calculate physical dimensions of the torso
            dy_torso = abs(shoulder_mid_y - hip_mid_y)
            dx_shoulders = abs(l_shoulder[0] - r_shoulder[0])
            
            # Ratio of Torso Height to Shoulder Width (scale-invariant)
            # Standing person ratio is > 1.5 (long torso). Lying down ratio drops < 0.65
            torso_ratio = dy_torso / max(1.0, dx_shoulders)
            
            # Calculate angle of torso relative to vertical (0 is vertical, 90 is horizontal)
            dx = hip_mid_x - shoulder_mid_x
            dy = hip_mid_y - shoulder_mid_y
            angle = math.degrees(math.atan2(abs(dx), abs(dy)))
            
            # A person has fallen if they are lying flat (low torso ratio) AND angled (>65 degrees)
            # OR if their aspect ratio is extremely horizontal (>1.6)
            is_fallen = (torso_ratio < 0.65 and angle > 65) or aspect_ratio > 1.6
            
            # Calculate dynamic confidence
            if is_fallen:
                conf = min(0.99, max(0.5, (angle / 90.0) * (1.0 - torso_ratio)))
            else:
                conf = 0.0
                
            return is_fallen, conf
            
        except Exception as e:
            # Fallback to pure bounding box aspect ratio
            is_fallen = aspect_ratio > 1.6
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
            
            # Extract keypoint coordinates and confidences if available
            keypoints_xy = results[0].keypoints.xy if results[0].keypoints is not None else [None]*len(boxes)
            keypoints_conf = results[0].keypoints.conf if (results[0].keypoints is not None and hasattr(results[0].keypoints, 'conf')) else [None]*len(boxes)
            
            for box, track_id, conf, kpts_xy, kpts_conf in zip(boxes, track_ids, confidences, keypoints_xy, keypoints_conf):
                x1, y1, x2, y2 = map(int, box)
                
                # Check for fall
                is_fallen, fall_conf = self.detect_fall(kpts_xy, kpts_conf, box)
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
                
                # Draw Box (Red if fallen, Blue if standing)
                box_color = (0, 0, 255) if is_fallen else (255, 240, 0)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), box_color, 2)
                
                # Draw Skeleton
                if kpts_xy is not None:
                    kpts_np = kpts_xy.cpu().numpy() if hasattr(kpts_xy, 'cpu') else kpts_xy
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
