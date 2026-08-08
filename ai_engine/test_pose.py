import cv2
import time
import sys
import os

# Add pipeline modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pipeline.ingest.rtsp_reader import CameraStreamReader
from pipeline.inference.pose_detector import YOLOPoseDetector

print("==============================================")
print(" GuardianAI - Pose Estimation & Fall Detection")
print("==============================================")
print("Press 'q' in the video window to quit.\n")

# Initialize the YOLO Pose model
detector = YOLOPoseDetector(model_path="yolov8n-pose.pt")

def frame_callback(camera_id, frame, current_fps, latency_ms):
    # Process the frame through the YOLO Pose model
    annotated_frame, detections, summary = detector.process_frame(frame)
    
    # Check if a fall was logged in this frame to print an alert
    for det in detections:
        if det.get("is_fallen"):
            print(f"[SECURITY ALERT] Person ID {det['track_id']} has FALLEN! (Confidence: {det['fall_confidence']:.2f})")

    # Display the resulting frame in an OpenCV window
    cv2.imshow("GuardianAI - Pose & Fall Detection", annotated_frame)
    
    # Check for 'q' key to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\n[Test] User requested exit. Shutting down...")
        reader.stop()
        cv2.destroyAllWindows()
        sys.exit(0)

# Connect to the default USB Web Camera (0)
camera_source = 0 

print(f"Initializing camera source: {camera_source}...")
reader = CameraStreamReader(camera_id="test-cam-1", stream_url=camera_source, target_fps=30)

# Start the capture loop in the background and pipe frames to our callback
reader.start(callback=frame_callback)

# Keep the main thread alive while the stream runs
try:
    while reader.running:
        time.sleep(1)
except KeyboardInterrupt:
    reader.stop()
    cv2.destroyAllWindows()
