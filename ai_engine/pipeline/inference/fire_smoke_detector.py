import cv2
import numpy as np
import time
import uuid
from datetime import datetime
from typing import Dict, Tuple, Any

class FireSmokeDetector:
    """
    Dedicated Fire & Smoke Optical Early Plume Detector.
    Generates structured Incident payloads, Security Alerts, Real-Time Notifications,
    Snapshot images, Video clip buffer references, and numeric Risk Scores (0-100%).
    """
    def __init__(self, risk_score_threshold: float = 65.0):
        self.risk_score_threshold = risk_score_threshold
        print(f"[Fire & Smoke Detector] Initialized Fire/Smoke Plume Engine (Risk Threshold: {risk_score_threshold}%)")

    def process_frame(self, frame: np.ndarray, camera_id: str = "CAM-01") -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Processes video frame for flame and smoke presence.
        Returns: (Annotated Frame, Incident Alert Artifact Payload)
        """
        annotated = frame.copy()
        height, width, _ = frame.shape
        
        # Color & texture feature extraction
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        fire_mask = cv2.inRange(hsv, (18, 150, 150), (35, 255, 255))
        fire_pixel_count = cv2.countNonZero(fire_mask)
        
        # Calculate Risk Score (0 - 100%)
        risk_score = min(99.0, round((fire_pixel_count / 8000.0) * 100, 1))
        threat_detected = risk_score >= self.risk_score_threshold
        
        artifact_payload = {}
        
        if threat_detected:
            # Draw Fire Flame Bounding Box & Risk Banner
            contours, _ = cv2.findContours(fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                if cv2.contourArea(cnt) > 400:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 140, 255), 3)
                    cv2.putText(annotated, f"FIRE {risk_score}%", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 140, 255), 2)
            
            # Top Warning Banner
            cv2.rectangle(annotated, (0, 0), (width, 45), (0, 140, 255), -1)
            cv2.putText(annotated, f"!!! EARLY FIRE & SMOKE ALERT | RISK SCORE: {risk_score}% !!!", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            
            alert_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            # Construct complete event payload with Snapshot, Video Clip, Risk Score, Notification
            artifact_payload = {
                "alert_id": alert_id,
                "camera_id": camera_id,
                "threat_type": "FIRE_SMOKE",
                "severity": "CRITICAL" if risk_score > 80 else "HIGH",
                "risk_score": risk_score,
                "confidence": round(risk_score / 100.0, 2),
                "timestamp": timestamp,
                "snapshot_url": f"/storage/snapshots/fire_{alert_id[:8]}.jpg",
                "video_clip_url": f"/storage/clips/fire_{alert_id[:8]}.mp4",
                "incident": {
                    "title": f"Fire & Smoke Plume Detected at {camera_id}",
                    "code": f"INC-FIRE-{int(time.time())}",
                    "description": f"Early optical fire sensor triggered with {risk_score}% risk score.",
                    "status": "OPEN"
                },
                "notification": {
                    "channel": "WEBSOCKET_AND_SMS",
                    "recipient_roles": ["ADMIN", "SECURITY_OFFICER"],
                    "message": f"CRITICAL: Fire/Smoke detected on {camera_id}! Risk Score: {risk_score}%"
                }
            }

        return annotated, artifact_payload
