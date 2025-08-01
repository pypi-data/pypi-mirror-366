"""
Simple Dataset Collector

Basit ama etkili dataset toplama sistemi.
Sadece temel sinyalleri kullanır.

Author: Promptlyzer Team
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional


class SimpleDatasetCollector:
    """
    Basit dataset collector - sadece en önemli sinyalleri toplar.
    
    Toplama kriterleri:
    1. Response süresi normal mi? (< 2 saniye)
    2. Error mesajı yok mu?
    3. Yeterince uzun cevap mı? (50+ karakter)
    4. Session ID ile takip
    """
    
    def __init__(self):
        self.collected_data = []
        self.sessions = {}  # session_id -> conversation history
    
    def collect(
        self,
        session_id: str,
        input_text: str,
        output_text: str,
        model: str,
        latency_ms: float,
        **extras
    ) -> bool:
        """
        Veriyi topla - basit kalite kontrolü ile.
        
        Returns:
            bool: Veri toplandı mı?
        """
        # Basit kalite kontrolleri
        if not self._is_good_quality(output_text, latency_ms):
            return False
        
        # Session'a ekle
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        # Veriyi kaydet
        data_point = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "input": input_text,
            "output": output_text,
            "model": model,
            "latency_ms": latency_ms,
            "conversation_number": len(self.sessions[session_id]) + 1
        }
        
        # Extras varsa ekle (prompt_name, version vs.)
        data_point.update(extras)
        
        self.sessions[session_id].append(data_point)
        self.collected_data.append(data_point)
        
        return True
    
    def _is_good_quality(self, output_text: str, latency_ms: float) -> bool:
        """
        Basit kalite kontrolü.
        
        Kriterler:
        - 50+ karakter output
        - 2 saniyeden kısa response time  
        - Error mesajı içermiyor
        """
        # Çok kısa cevapları alma
        if len(output_text) < 50:
            return False
        
        # Çok yavaş cevapları alma (timeout vs. olabilir)
        if latency_ms > 2000:
            return False
        
        # Error mesajları kontrolü
        error_words = ["error", "failed", "exception", "sorry, i cannot", "i'm unable to"]
        output_lower = output_text.lower()
        if any(error in output_lower for error in error_words):
            return False
        
        return True
    
    def get_good_conversations(self, min_turns: int = 2) -> List[Dict]:
        """
        En az N turn'lü iyi konuşmaları getir.
        Bunlar genelde kaliteli oluyor çünkü kullanıcı devam etmiş.
        """
        good_convos = []
        
        for session_id, messages in self.sessions.items():
            if len(messages) >= min_turns:
                # Bu session iyi, kullanıcı devam etmiş
                for msg in messages:
                    msg["is_good_quality"] = True
                    msg["reason"] = f"part_of_{len(messages)}_turn_conversation"
                    good_convos.append(msg)
        
        return good_convos
    
    def export_dataset(self) -> Dict:
        """
        Dataset'i export et - sadece kaliteli olanları.
        """
        good_data = self.get_good_conversations()
        
        # QA pairs formatına çevir
        qa_pairs = []
        for data in good_data:
            qa_pairs.append({
                "question": data["input"],
                "answer": data["output"],
                "metadata": {
                    "model": data["model"],
                    "session_id": data["session_id"],
                    "turn_number": data["conversation_number"]
                }
            })
        
        return {
            "name": "Production Dataset",
            "description": "Automatically collected from production usage",
            "type": "qa_dataset",
            "qa_pairs": qa_pairs,
            "stats": {
                "total_collected": len(self.collected_data),
                "quality_filtered": len(good_data),
                "unique_sessions": len(self.sessions)
            }
        }
    
    def save_to_file(self, filename: str = "collected_dataset.json"):
        """Dataset'i dosyaya kaydet."""
        dataset = self.export_dataset()
        with open(filename, "w") as f:
            json.dump(dataset, f, indent=2)
        return filename