import cv2
import time
import sys
import os
import requests
import uuid
from typing import Optional
import threading

try:
    from flask import Flask, Response
except ImportError:
    print("[ERROR] Flask not found! Run: pip install flask")
    Flask = None

# Add pipeline modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pipeline.ingest.rtsp_reader import CameraStreamReader
from pipeline.inference.pose_detector import YOLOPoseDetector
from pipeline.inference.yolo_detector import YOLO11PersonDetector
from pipeline.inference.intrusion_counter import IntrusionAndCounterEngine

BACKEND_URL = "http://localhost:8000"
CAMERA_NAME = "Local WebCam"

# Thread-safe MJPEG streamer setup
latest_frame = None
frame_lock = threading.Lock()

if Flask is not None:
    app = Flask(__name__)

    def get_frame():
        global latest_frame
        while True:
            with frame_lock:
                if latest_frame is None:
                    time.sleep(0.01)
                    continue
                ret, jpeg = cv2.imencode('.jpg', latest_frame)
                if not ret:
                    time.sleep(0.01)
                    continue
                frame_bytes = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.03) # Cap stream to ~30 FPS

    @app.route('/stream')
    def stream():
        return Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def run_server():
        try:
            app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)
        except Exception as e:
            print(f"[Streaming Server Error] {e}")

    print("[Pipeline] Launching background streaming server on port 5000...")
    threading.Thread(target=run_server, daemon=True).start()

print("==============================================")
print(" GuardianAI - Live Dashboard Pipeline")
print("==============================================")
print("Checking backend API connection...")

# 1. Handshake with backend to register/fetch camera ID
camera_id = None
retries = 5
for i in range(retries):
    try:
        # Check existing cameras
        response = requests.get(f"{BACKEND_URL}/api/v1/cameras")
        if response.status_code == 200:
            cameras = response.json()
            for cam in cameras:
                if cam["name"] == CAMERA_NAME:
                    camera_id = cam["id"]
                    print(f"[Pipeline] Connected! Found existing camera: {CAMERA_NAME} (ID: {camera_id})")
                    break
            
            # If not found, register it
            if not camera_id:
                print(f"[Pipeline] Camera '{CAMERA_NAME}' not registered. Registering now...")
                reg_response = requests.post(
                    f"{BACKEND_URL}/api/v1/cameras",
                    json={
                        "name": CAMERA_NAME,
                        "rtsp_url": "0",
                        "location_zone": "Zone A",
                        "active_detectors": {
                            "pose": True,
                            "fall": True,
                            "intrusion": True,
                            "weapon": True,
                            "fire": True
                        }
                    }
                )
                if reg_response.status_code == 201:
                    camera_id = reg_response.json()["id"]
                    print(f"[Pipeline] Successfully registered camera: {CAMERA_NAME} (ID: {camera_id})")
                else:
                    print(f"[Pipeline] Failed to register camera: {reg_response.text}")
            break
    except requests.exceptions.ConnectionError:
        print(f"[Pipeline] Backend not reachable. Retrying in 2s ({i+1}/{retries})...")
        time.sleep(2)

if not camera_id:
    # If backend is completely down, fallback to a dummy UUID so the script doesn't crash
    camera_id = str(uuid.uuid4())
    print(f"[Pipeline] WARNING: Could not connect to backend. Running in OFFLINE mode with dummy camera ID: {camera_id}")
else:
    print(f"[Pipeline] Connected to backend! Live alerts will be sent in real-time.")

# Initialize the YOLO Pose model
detector = YOLOPoseDetector(model_path="yolov8n-pose.pt")

# Initialize the YOLO Object model (detects knives, backpacks, suitcases)
object_detector = YOLO11PersonDetector(model_path="yolov8n.pt")

# Initialize the Intrusion Counter
intrusion_engine = IntrusionAndCounterEngine()

# Keep track of recently sent alerts to avoid flooding the API
last_alert_time = {}

def send_dashboard_alert(threat_type: str, severity: str, confidence: float, bbox: list):
    """Sends a POST request to log the security alert in the backend database."""
    try:
        # Convert numpy types to native Python types to avoid JSON serialization crash
        native_confidence = float(confidence)
        native_bbox = [int(x) for x in bbox]
        
        payload = {
            "camera_id": camera_id,
            "threat_type": threat_type,
            "severity": severity,
            "confidence": round(native_confidence, 2),
            "snapshot_url": "https://images.unsplash.com/photo-1557597774-9d273605dfa9?q=80&w=300", # Placeholder mock snapshot
            "bounding_boxes": {"bbox": native_bbox}
        }
        res = requests.post(f"{BACKEND_URL}/api/v1/alerts", json=payload)
        if res.status_code == 200:
            print(f"[API PUSH] Successfully logged {threat_type} alert on dashboard!")
        else:
            print(f"[API ERROR] Failed to send alert: {res.text}")
    except Exception as e:
        print(f"[API ERROR] Connection failure while pushing alert: {e}")

def frame_callback(camera_id, frame, current_fps, latency_ms):
    global latest_frame
    height, width = frame.shape[:2]
    fence_line = ((50, int(height / 2)), (width - 50, int(height / 2)))
    current_time = time.time()
    
    # 1. Run Pose & Fall Detection
    pose_frame, detections_pose, summary_pose = detector.process_frame(frame)
    
    # 2. Run General Object Detection (Knife, Bags, Vehicles)
    final_frame, detections_obj, summary_obj = object_detector.process_frame(pose_frame)
    
    # 3. Process Fall Alerts and Line Crossings (using Pose tracking)
    for det in detections_pose:
        track_id = det["track_id"]
        bbox = det["bbox"]
        
        # A. Fall Alerts
        if det.get("is_fallen"):
            alert_key = f"fall_{track_id}"
            if current_time - last_alert_time.get(alert_key, 0) > 10:
                print(f"[SECURITY ALERT] Fall detected for ID {track_id}")
                send_dashboard_alert(
                    threat_type="FALL_DETECTION",
                    severity="CRITICAL",
                    confidence=det.get("fall_confidence", 0.9),
                    bbox=bbox
                )
                last_alert_time[alert_key] = current_time
                
        # B. Line Crossing / Intrusion Alerts (Feet centroid)
        centroid = (int((bbox[0] + bbox[2]) / 2), bbox[3])
        event = intrusion_engine.check_line_crossing(
            track_id=track_id,
            centroid=centroid,
            line_start=fence_line[0],
            line_end=fence_line[1]
        )
        if event:
            alert_key = f"intrusion_{track_id}_{event}"
            if current_time - last_alert_time.get(alert_key, 0) > 10:
                print(f"[SECURITY ALERT] Perimeter crossed ({event}) by ID {track_id}")
                send_dashboard_alert(
                    threat_type="INTRUSION_DETECTION",
                    severity="HIGH",
                    confidence=0.95,
                    bbox=bbox
                )
                last_alert_time[alert_key] = current_time

    # 4. Process General Objects (Knife, Crowd Count)
    person_count = len(detections_pose)
    for det in detections_obj:
        label = det["label"]
        bbox = det["bbox"]
            
        # A. Weapon Detection (Knife)
        if label == "knife":
            alert_key = f"weapon_{det['track_id']}"
            if current_time - last_alert_time.get(alert_key, 0) > 10:
                print(f"[SECURITY ALERT] WEAPON DETECTED: KNIFE (ID {det['track_id']})")
                send_dashboard_alert(
                    threat_type="WEAPON_DETECTION",
                    severity="CRITICAL",
                    confidence=det["confidence"],
                    bbox=bbox
                )
                last_alert_time[alert_key] = current_time
                
            # Draw Flashing red box around the weapon
            cv2.rectangle(final_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 3)
            cv2.putText(final_frame, "WEAPON THREAT", (bbox[0], bbox[1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
    # B. Crowd Congestion Warning (> 3 people)
    if person_count > 3:
        alert_key = "crowd_congestion"
        if current_time - last_alert_time.get(alert_key, 0) > 15:
            print(f"[SECURITY WARNING] Crowd congestion detected: {person_count} persons")
            send_dashboard_alert(
                threat_type="CROWD_CONGESTION",
                severity="MEDIUM",
                confidence=min(0.99, 0.7 + (person_count * 0.05)),
                bbox=[0, 0, width, height]
            )
            last_alert_time[alert_key] = current_time

    # 5. HSV Plume Fire & Smoke Detection Heuristic
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Bright orange/red flicker range
    fire_mask = cv2.inRange(hsv, (18, 150, 150), (35, 255, 255))
    fire_pixels = cv2.countNonZero(fire_mask)
    if fire_pixels > 5000:
        # Draw red border on frame and show text
        cv2.rectangle(final_frame, (0, 0), (width, height), (0, 0, 255), 8)
        cv2.putText(final_frame, "!!! FIRE/SMOKE DETECTED !!!", (int(width/2) - 150, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
        
        alert_key = "fire_alert"
        if current_time - last_alert_time.get(alert_key, 0) > 10:
            print("[SECURITY ALERT] Flame plume detected in frame!")
            send_dashboard_alert(
                threat_type="FIRE_DETECTION",
                severity="CRITICAL",
                confidence=min(0.99, float(fire_pixels / 10000.0)),
                bbox=[0, 0, width, height]
            )
            last_alert_time[alert_key] = current_time

    # Draw the virtual fence line on top
    final_frame = intrusion_engine.draw_roi_and_lines(
        frame=final_frame, 
        polygon_zone=[],
        virtual_fence_line=fence_line
    )
    
    # Save frame for background Flask streamer thread-safely
    with frame_lock:
        latest_frame = final_frame.copy()

    # Display the live window
    cv2.imshow("GuardianAI - Live Dashboard Pipeline", final_frame)
    
    # Check for 'q' key to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\n[Pipeline] Shutting down...")
        reader.stop()
        cv2.destroyAllWindows()
        sys.exit(0)

# Connect to default camera source (webcam index 0)
camera_source = 0 
print(f"Starting camera source {camera_source}...")
reader = CameraStreamReader(camera_id="test-cam-1", stream_url=camera_source, target_fps=30)
reader.start(callback=frame_callback)

try:
    while reader.running:
        time.sleep(1)
except KeyboardInterrupt:
    reader.stop()
    cv2.destroyAllWindows()
