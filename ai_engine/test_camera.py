import cv2
import time
import sys
import os

# Add pipeline modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pipeline.ingest.rtsp_reader import CameraStreamReader
from pipeline.inference.yolo_detector import YOLO11PersonDetector
from pipeline.inference.intrusion_counter import IntrusionAndCounterEngine

print("==============================================")
print(" GuardianAI - Advanced Surveillance Test Tool")
print("==============================================")
print("Press 'q' in the video window to quit.\n")

# Initialize the YOLO model
detector = YOLO11PersonDetector(use_tensorrt=False)

# Initialize the Intrusion Counter
intrusion_engine = IntrusionAndCounterEngine()

# Define a virtual fence line (x1, y1) to (x2, y2)
# We will draw this roughly horizontally across the middle of a standard 640x480 webcam feed
fence_line = ((50, 240), (590, 240))

def frame_callback(camera_id, frame, current_fps, latency_ms):
    # Dynamically adjust fence line if frame size differs from 640x480
    height, width = frame.shape[:2]
    dynamic_fence_line = ((50, int(height/2)), (width-50, int(height/2)))
    
    # Process the frame through the YOLO model
    annotated_frame, detections, summary = detector.process_frame(frame)
    
    # Run intrusion counting for every detected object
    for det in detections:
        track_id = det["track_id"]
        centroid = det["centroid"]
        
        event = intrusion_engine.check_line_crossing(
            track_id=track_id,
            centroid=centroid,
            line_start=dynamic_fence_line[0],
            line_end=dynamic_fence_line[1]
        )
        if event:
            print(f"[SECURITY ALERT] Object {track_id} ({det['label'].upper()}) crossed the perimeter: {event}")

    # Draw the virtual fence and the HUD on top of the YOLO annotations
    final_frame = intrusion_engine.draw_roi_and_lines(
        frame=annotated_frame, 
        polygon_zone=[], # Skipping polygon zone for this demo
        virtual_fence_line=dynamic_fence_line
    )
    
    # Display the resulting frame in an OpenCV window
    cv2.imshow("GuardianAI - Full Surveillance Mode", final_frame)
    
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
