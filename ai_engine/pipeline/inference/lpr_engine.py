import cv2
import numpy as np
import time
from typing import Dict, List, Tuple, Any

class LicensePlateRecognizer:
    """
    ALPR (Automatic License Plate Recognition) Engine using PaddleOCR backend.
    Detects bounding boxes of license plates and reads the alphanumeric characters.
    Links with backend vehicle search API to check against blacklists.
    """
    def __init__(self, confidence_threshold: float = 0.85):
        self.confidence_threshold = confidence_threshold
        # Simulating PaddleOCR initialization
        print(f"[ALPR Engine] Initialized PaddleOCR License Plate Recognizer (Confidence Threshold: {confidence_threshold})")

    def process_plate_crop(self, plate_image: np.ndarray) -> Dict[str, Any]:
        """
        Runs OCR on a cropped image of a license plate.
        Returns plate text, confidence, and timestamp.
        """
        # Simulated OCR for demonstration without heavy PaddleOCR binary dependencies
        simulated_plates = ["NVI-8829", "KA-04-MB-9012", "TEX-9910", "UK-07-AZ-1102", "DL-8C-NB-1022"]
        plate_text = np.random.choice(simulated_plates)
        confidence = round(np.random.uniform(0.88, 0.99), 2)
        
        # Simulated blacklist check
        is_blacklisted = plate_text in ["KA-04-MB-9012", "TEX-9910"]
        
        return {
            "plate_number": plate_text,
            "confidence": confidence,
            "is_blacklisted": is_blacklisted,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def detect_and_read(self, frame: np.ndarray, vehicle_bboxes: List[List[int]]) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Takes full frame and detected vehicle bounding boxes.
        Finds license plates within those vehicle crops and runs OCR.
        """
        annotated_frame = frame.copy()
        alpr_results = []
        
        for bbox in vehicle_bboxes:
            x1, y1, x2, y2 = bbox
            # Typically, plate is in the lower half of the vehicle bounding box
            # For simulation, we just run the OCR process to get a mock result
            ocr_result = self.process_plate_crop(frame[y1:y2, x1:x2])
            
            # Append bounding box mapping to result
            ocr_result["vehicle_bbox"] = bbox
            alpr_results.append(ocr_result)
            
            # Annotate ALPR result on frame
            plate_text = ocr_result["plate_number"]
            conf = ocr_result["confidence"]
            bg_color = (0, 0, 255) if ocr_result["is_blacklisted"] else (0, 255, 0)
            
            hud_text = f"ALPR: {plate_text} ({int(conf*100)}%)"
            cv2.rectangle(annotated_frame, (x1, y2), (x1 + 200, y2 + 25), bg_color, -1)
            cv2.putText(annotated_frame, hud_text, (x1 + 5, y2 + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0) if not ocr_result["is_blacklisted"] else (255,255,255), 2, cv2.LINE_AA)

        return annotated_frame, alpr_results
