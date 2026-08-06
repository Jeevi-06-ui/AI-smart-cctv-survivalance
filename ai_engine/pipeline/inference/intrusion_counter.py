import cv2
import numpy as np
from typing import Dict, List, Tuple, Any

class IntrusionAndCounterEngine:
    """
    Virtual Fence, Polygon Restricted Zone, Directional Line Crossing,
    and Dynamic People Counting Security Engine.
    """
    def __init__(self):
        # People Count metrics
        self.count_in = 0
        self.count_out = 0
        
        # Track crossed history to prevent duplicate counts: track_id -> side (+1 or -1)
        self.crossed_ids = {}
        print("[Intrusion Engine] Initialized Virtual Fence & Line Crossing Counter.")

    def check_line_crossing(
        self, 
        track_id: int, 
        centroid: Tuple[int, int], 
        line_start: Tuple[int, int], 
        line_end: Tuple[int, int]
    ) -> Optional[str]:
        """
        Evaluates line crossing vector equation for directional IN/OUT counting.
        """
        x, y = centroid
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Cross product to determine side of line: (x2-x1)*(y-y1) - (y2-y1)*(x-x1)
        side = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
        current_side = 1 if side > 0 else -1
        
        event = None
        if track_id in self.crossed_ids:
            prev_side = self.crossed_ids[track_id]
            if prev_side != current_side:
                if prev_side == -1 and current_side == 1:
                    self.count_in += 1
                    event = "IN"
                elif prev_side == 1 and current_side == -1:
                    self.count_out += 1
                    event = "OUT"
                self.crossed_ids[track_id] = current_side
        else:
            self.crossed_ids[track_id] = current_side
            
        return event

    def draw_roi_and_lines(
        self, 
        frame: np.ndarray, 
        polygon_zone: List[Tuple[int, int]], 
        virtual_fence_line: Tuple[Tuple[int, int], Tuple[int, int]]
    ) -> np.ndarray:
        """Annotates Restricted Polygon Zone and Virtual Fence Line on frame."""
        annotated = frame.copy()
        
        # 1. Draw Restricted Polygon Zone (Glassmorphic Translucent Red Fill)
        if polygon_zone and len(polygon_zone) >= 3:
            pts = np.array(polygon_zone, np.int32).reshape((-1, 1, 2))
            overlay = annotated.copy()
            cv2.fillPoly(overlay, [pts], (0, 0, 220))
            cv2.addWeighted(overlay, 0.25, annotated, 0.75, 0, annotated)
            cv2.polylines(annotated, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
            
            # Label
            cv2.putText(annotated, "RESTRICTED ZONE (POLYGON A)", (pts[0][0][0] + 10, pts[0][0][1] + 25), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # 2. Draw Virtual Fence Line (Neon Yellow Directional Line)
        if virtual_fence_line:
            p1, p2 = virtual_fence_line
            cv2.line(annotated, p1, p2, (0, 240, 255), 3)
            cv2.circle(annotated, p1, 5, (0, 240, 255), -1)
            cv2.circle(annotated, p2, 5, (0, 240, 255), -1)
            
            # Counter HUD
            counter_hud = f"VIRTUAL FENCE | IN: {self.count_in} | OUT: {self.count_out}"
            cv2.putText(annotated, counter_hud, (p1[0] + 10, p1[1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 240, 255), 2)

        return annotated
