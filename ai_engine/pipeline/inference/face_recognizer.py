import numpy as np
import time
from typing import Dict, List, Tuple, Optional, Any

class InsightFaceRecognizer:
    """
    InsightFace (ArcFace ResNet-100) Face Recognition & Vector Matching Engine.
    Extracts 512-dimensional face embeddings, calculates cosine similarity against
    PgVector database embeddings, categorizes subjects (EMPLOYEE, VISITOR, BLACKLIST, UNKNOWN),
    and triggers security alerts.
    """
    def __init__(self, similarity_threshold: float = 0.60):
        self.similarity_threshold = similarity_threshold
        # Enrolled Watchlist Cache: person_id -> Dict
        self.enrolled_watchlist: List[Dict[str, Any]] = []
        print(f"[InsightFace Engine] Initialized ArcFace 512d Recognizer (Similarity Threshold: {similarity_threshold})")
        
        # Seed mock enrolled subjects for immediate verification
        self._seed_watchlist()

    def _seed_watchlist(self):
        """Seed enrolled watchlist faces with synthetic 512d vectors."""
        # 1. Blacklisted Target
        blacklisted_vec = np.random.randn(512).astype(np.float32)
        blacklisted_vec /= np.linalg.norm(blacklisted_vec)
        self.enrolled_watchlist.append({
            "person_id": "PER-BLK-001",
            "name": "Marcus Vance (Wanted Subject)",
            "category": "BLACKLIST",
            "embedding": blacklisted_vec
        })
        
        # 2. VIP Employee
        vip_vec = np.random.randn(512).astype(np.float32)
        vip_vec /= np.linalg.norm(vip_vec)
        self.enrolled_watchlist.append({
            "person_id": "PER-EMP-104",
            "name": "Dr. Sarah Connor",
            "category": "EMPLOYEE",
            "embedding": vip_vec
        })

    def enroll_face(self, person_id: str, name: str, category: str, embedding_vector: np.ndarray) -> Dict[str, Any]:
        """Enrolls a new person and stores their 512-dim embedding."""
        norm_embedding = embedding_vector / np.linalg.norm(embedding_vector)
        record = {
            "person_id": person_id,
            "name": name,
            "category": category, # BLACKLIST, VISITOR, EMPLOYEE
            "embedding": norm_embedding
        }
        self.enrolled_watchlist.append(record)
        print(f"[InsightFace Engine] Enrolled new subject '{name}' ({category}) with 512d embedding.")
        return record

    def extract_embedding(self, face_crop: np.ndarray) -> np.ndarray:
        """Simulates 512d ArcFace feature vector extraction from face crop."""
        vec = np.random.randn(512).astype(np.float32)
        return vec / np.linalg.norm(vec)

    def match_face(self, face_embedding: np.ndarray) -> Tuple[str, str, float, bool]:
        """
        Calculates cosine similarity between input embedding and enrolled watchlist.
        Returns: (Name, Category, Similarity Score, Trigger Alert Flag)
        """
        best_match_name = "UNKNOWN"
        best_category = "UNKNOWN"
        best_similarity = 0.0
        trigger_alert = False
        
        norm_input = face_embedding / np.linalg.norm(face_embedding)
        
        for record in self.enrolled_watchlist:
            # Cosine similarity dot product of normalized vectors
            sim = float(np.dot(norm_input, record["embedding"]))
            if sim > best_similarity:
                best_similarity = sim
                if sim >= self.similarity_threshold:
                    best_match_name = record["name"]
                    best_category = record["category"]
                    
        # Trigger critical security alert if blacklisted subject identified
        if best_category == "BLACKLIST":
            trigger_alert = True
            
        return best_match_name, best_category, round(best_similarity, 3), trigger_alert

    def process_face_crop(self, face_crop: np.ndarray) -> Dict[str, Any]:
        """Full pipeline for a detected face crop."""
        emb = self.extract_embedding(face_crop)
        name, category, sim, alert_flag = self.match_face(emb)
        
        return {
            "name": name,
            "category": category,
            "similarity": sim,
            "trigger_alert": alert_flag,
            "embedding_512": emb.tolist()[:10] # Truncated for JSON output
        }
