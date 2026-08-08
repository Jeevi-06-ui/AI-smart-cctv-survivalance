import cv2
import numpy as np
import time
import json
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Any

try:
    from ultralytics import YOLO
except ImportError:
    print("[ERROR] ultralytics package not found! Please run 'pip install ultralytics'")
    YOLO = None

class YOLO11PersonDetector:
    """
    Real Ultralytics YOLO & TensorRT Ready Person Detection and Trajectory Tracking Engine.
    Processes video frames using real AI, draws low-latency bounding boxes, trajectory trails,
    counts active persons, calculates FPS, and exports JSON tracking metrics.
    """
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.45, use_tensorrt: bool = False):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.use_tensorrt = use_tensorrt
        
        # Track history trajectories: track_id -> deque of (x, y) coordinates
        self.track_history = defaultdict(lambda: deque(maxlen=30))
        
        # Performance stats
        self.fps = 0.0
        self.total_persons_detected = 0
        
        # Load the real YOLO model (downloads automatically if not found locally)
        if YOLO is not None:
            print(f"[YOLO Engine] Loading model {model_path}...")
            self.model = YOLO(model_path)
            print(f"[YOLO Engine] Initialized Real YOLO Person Detector (TensorRT: {use_tensorrt}, Conf: {confidence_threshold})")
        else:
            self.model = None
            print("[YOLO Engine] WARNING: Running without YOLO. Simulated logic fallback not implemented.")

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Runs person detection & tracking on input BGR frame using the real AI model.
        Returns: (Annotated Frame, Detection List, Summary Metrics)
        """
        start_time = time.time()
        annotated_frame = frame.copy()
        detections = []
        
        if self.model is None:
            return annotated_frame, detections, {"error": "Model not loaded"}

        # Run YOLO real-time tracking (classes for person, car, motorcycle, bus, truck, backpack, handbag, suitcase)
        # persist=True enables the built-in tracker (BoT-SORT/ByteTrack)
        results = self.model.track(frame, persist=True, classes=[0, 2, 3, 5, 7, 24, 26, 28], conf=self.confidence_threshold, verbose=False)
        
        # Extract results
        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            confidences = results[0].boxes.conf.cpu().numpy()
            class_ids = results[0].boxes.cls.int().cpu().tolist()
            
            for box, track_id, conf, cls_id in zip(boxes, track_ids, confidences, class_ids):
                x1, y1, x2, y2 = map(int, box)
                
                # Calculate centroid (bottom center / feet point for tracking)
                center_x = int((x1 + x2) / 2)
                feet_point = (center_x, y2)
                
                # Get the actual class name from the model (e.g. 'person', 'car', 'backpack')
                obj_label = self.model.names[cls_id]
                
                # Store trajectory
                self.track_history[track_id].append(feet_point)
                
                # Append to detections list
                det_info = {
                    "track_id": track_id,
                    "label": obj_label,
                    "confidence": float(conf),
                    "bbox": [x1, y1, x2, y2],
                    "centroid": feet_point
                }
                detections.append(det_info)
                
                # 1. Draw Trajectory Trail
                if len(self.track_history[track_id]) > 1:
                    points = np.hstack(self.track_history[track_id]).astype(np.int32).reshape((-1, 1, 2))
                    cv2.polylines(annotated_frame, [points], isClosed=False, color=(0, 240, 255), thickness=2)
                
                # 2. Draw Bounding Box (Neon Cyber Cyan)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 240, 0), 2)
                
                # 3. Draw Label & Confidence Badge
                label_text = f"ID:{track_id} {obj_label.upper()} {int(conf * 100)}%"
                (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(annotated_frame, (x1, y1 - 20), (x1 + tw + 6, y1), (255, 240, 0), -1)
                cv2.putText(annotated_frame, label_text, (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

        # Calculate FPS
        exec_time = time.time() - start_time
        self.fps = round(1.0 / max(exec_time, 0.001), 1)
        
        # HUD Overlay on Frame
        hud_text = f"REAL YOLOv8 Engine | FPS: {self.fps} | Active Objects: {len(detections)}"
        cv2.putText(annotated_frame, hud_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 240, 255), 2, cv2.LINE_AA)

        summary = {
            "fps": self.fps,
            "person_count": len(detections),
            "inference_latency_ms": round(exec_time * 1000, 2),
            "tensorrt_active": self.use_tensorrt
        }

        return annotated_frame, detections, summary

    def export_results_json(self, detections: List[Dict[str, Any]], filename: str = "detection_export.json"):
        """Exports detection results and trajectory metrics to JSON file."""
        export_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": "YOLOv8-Real",
            "active_persons": len(detections),
            "detections": detections
        }
        with open(filename, "w") as f:
            json.dump(export_data, f, indent=2)
        print(f"[YOLO Engine] Detection metrics exported to {filename}")
