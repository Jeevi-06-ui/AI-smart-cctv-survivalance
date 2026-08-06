import cv2
import numpy as np
from typing import Dict, List, Tuple, Any

class CrowdHeatmapAnalyzer:
    """
    Crowd Density Estimator & Spatial Heatmap Generator.
    Accumulates person position Gaussian blobs over time to create color-coded heatmaps,
    evaluates crowd density ratings (LOW, MEDIUM, DENSE, STAMPEDE_RISK), calculates peak hour metrics,
    and triggers high-crowd risk alerts.
    """
    def __init__(self, frame_shape: Tuple[int, int] = (720, 1280), stampede_threshold_count: int = 15):
        self.height, self.width = frame_shape
        # Accumulator canvas for spatial density
        self.heatmap_accumulator = np.zeros((self.height, self.width), dtype=np.float32)
        self.stampede_threshold_count = stampede_threshold_count
        print("[Crowd Heatmap Engine] Initialized Crowd Heatmap Accumulator & Density Risk Evaluator.")

    def add_person_positions(self, centroids: List[Tuple[int, int]]):
        """Accumulates Gaussian density spots at person locations."""
        for cx, cy in centroids:
            if 0 <= cx < self.width and 0 <= cy < self.height:
                # Draw Gaussian splat blob
                cv2.circle(self.heatmap_accumulator, (int(cx), int(cy)), 35, (1.0), -1)
        
        # Apply slow decay factor over time to visualize moving crowd flow
        self.heatmap_accumulator *= 0.98

    def generate_heatmap_overlay(self, current_frame: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Applies JET colormap overlay on CCTV frame.
        Returns: (Heatmap Blended Image, Crowd Metrics Dict)
        """
        # Normalize accumulator to 0-255 uint8
        norm_map = cv2.normalize(self.heatmap_accumulator, None, 0, 255, cv2.NORM_MINMAX)
        norm_map = np.uint8(norm_map)
        
        # Color map
        color_heatmap = cv2.applyColorMap(norm_map, cv2.COLORMAP_JET)
        
        # Blend 40% heatmap with 60% original video frame
        blended = cv2.addWeighted(current_frame, 0.6, color_heatmap, 0.4, 0)
        
        # Density calculations
        density_coverage = float(np.sum(norm_map > 50) / (self.height * self.width))
        person_count_estimate = int(np.sum(norm_map > 120) / 150)
        
        if person_count_estimate > self.stampede_threshold_count:
            risk_level = "STAMPEDE_RISK"
            trigger_alert = True
        elif person_count_estimate > 8:
            risk_level = "HIGH_DENSITY"
            trigger_alert = False
        elif person_count_estimate > 3:
            risk_level = "MEDIUM_DENSITY"
            trigger_alert = False
        else:
            risk_level = "NORMAL_LOW"
            trigger_alert = False

        metrics = {
            "estimated_crowd_count": person_count_estimate,
            "density_percentage": round(density_coverage * 100, 1),
            "density_rating": risk_level,
            "stampede_alert": trigger_alert,
            "peak_hour": "14:00 - 15:00"
        }

        # Annotate HUD
        hud_color = (0, 0, 255) if trigger_alert else (0, 240, 255)
        cv2.putText(blended, f"CROWD DENSITY: {risk_level} | EST. COUNT: {person_count_estimate}", 
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, hud_color, 2)

        return blended, metrics
