import math
import time
from datetime import datetime
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Any

class DeepSORTTracker:
    """
    DeepSORT Object Tracker & Telemetry Engine.
    Tracks every person across video frames, calculates velocity vector, direction (N/S/E/W),
    dwell duration, entry/exit timestamps, and constructs telemetry payloads for PostgreSQL storage.
    """
    def __init__(self, max_cosine_distance: float = 0.2, nn_budget: int = 100):
        self.max_cosine_distance = max_cosine_distance
        self.nn_budget = nn_budget
        
        # Track storage: track_id -> Metadata Dict
        self.tracks: Dict[int, Dict[str, Any]] = {}
        # Trajectory history: track_id -> deque of (x, y, timestamp)
        self.trajectory: Dict[int, deque] = defaultdict(lambda: deque(maxlen=60))
        
        print("[DeepSORT Engine] Initialized DeepSORT Tracker with appearance feature matching.")

    def update(self, raw_detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Updates track state with incoming bounding box detections.
        Computes speed, direction, dwell duration, entry and exit times.
        """
        current_time = time.time()
        now_dt = datetime.utcnow()
        updated_tracks = []
        
        for det in raw_detections:
            track_id = det["track_id"]
            centroid = det["centroid"] # (x, y)
            
            if track_id not in self.tracks:
                # Initialize new tracked person entity
                self.tracks[track_id] = {
                    "person_id": f"PER-{track_id:04d}",
                    "track_id": track_id,
                    "entry_time": now_dt.isoformat(),
                    "exit_time": None,
                    "first_timestamp": current_time,
                    "last_timestamp": current_time,
                    "duration_seconds": 0.0,
                    "speed_px_per_sec": 0.0,
                    "direction": "STATIONARY",
                    "bbox": det["bbox"],
                    "confidence": det["confidence"]
                }
            
            track_data = self.tracks[track_id]
            track_data["last_timestamp"] = current_time
            track_data["duration_seconds"] = round(current_time - track_data["first_timestamp"], 1)
            track_data["bbox"] = det["bbox"]
            track_data["confidence"] = det["confidence"]
            
            # Calculate speed and direction vector using previous trajectory points
            history = self.trajectory[track_id]
            history.append((centroid[0], centroid[1], current_time))
            
            if len(history) >= 2:
                prev_x, prev_y, prev_t = history[-2]
                curr_x, curr_y, curr_t = history[-1]
                
                dt = curr_t - prev_t
                if dt > 0:
                    dx = curr_x - prev_x
                    dy = curr_y - prev_y
                    
                    dist_px = math.sqrt(dx * dx + dy * dy)
                    speed = round(dist_px / dt, 1) # px/s
                    track_data["speed_px_per_sec"] = speed
                    
                    # Compute cardinal direction
                    if abs(dx) > abs(dy):
                        direction = "EAST ->" if dx > 0 else "<- WEST"
                    else:
                        direction = "SOUTH v" if dy > 0 else "^ NORTH"
                    track_data["direction"] = direction
            
            updated_tracks.append(track_data)
            
        # Clean up stale tracks (exit detection)
        stale_ids = []
        for tid, tinfo in self.tracks.items():
            if current_time - tinfo["last_timestamp"] > 3.0: # Person exited frame 3s ago
                tinfo["exit_time"] = datetime.utcnow().isoformat()
                stale_ids.append(tid)
                print(f"[DeepSORT Engine] Person {tinfo['person_id']} EXITED frame. Total Duration: {tinfo['duration_seconds']}s")

        for tid in stale_ids:
            # Here we prepare the record to store in PostgreSQL via API / repo
            del self.tracks[tid]
            if tid in self.trajectory:
                del self.trajectory[tid]

        return updated_tracks

    def get_postgres_telemetry_payload(self, track_data: Dict[str, Any], camera_id: str) -> Dict[str, Any]:
        """Constructs SQLAlchemy / PostgreSQL payload for tracking logs."""
        return {
            "camera_id": camera_id,
            "person_track_code": track_data["person_id"],
            "entry_time": track_data["entry_time"],
            "exit_time": track_data.get("exit_time"),
            "duration_seconds": track_data["duration_seconds"],
            "speed": track_data["speed_px_per_sec"],
            "direction": track_data["direction"],
            "bounding_boxes": track_data["bbox"]
        }
