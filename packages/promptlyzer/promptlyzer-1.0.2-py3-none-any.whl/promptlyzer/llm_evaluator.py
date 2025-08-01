"""
LLM-based Dataset Evaluator

LLM kullanarak dataset kalitesini değerlendirme.
Maliyet optimizasyonu için batch processing kullanır.

Author: Promptlyzer Team
"""

import json
from typing import List, Dict, Tuple


class LLMEvaluator:
    """
    LLM ile dataset kalite değerlendirmesi
    """
    
    def __init__(self, inference_manager):
        self.inference = inference_manager
        self.evaluation_cache = {}
        
    def evaluate_single_pair(self, input_text: str, output_text: str) -> Tuple[bool, str]:
        """
        TEK bir Q&A pair'i değerlendir - PAHALI YÖNTEM!
        
        Örnek:
        Input: "Python'da liste nasıl oluşturulur?"
        Output: "Python'da liste şöyle oluşturulur: my_list = [1, 2, 3]"
        
        LLM'e sorar: Bu iyi bir cevap mı?
        """
        
        prompt = f"""
        Değerlendir: Bu soru-cevap çifti kaliteli mi?
        
        SORU: {input_text}
        CEVAP: {output_text}
        
        Kriterler:
        - Cevap soruyu doğru yanıtlıyor mu?
        - Cevap yeterince açıklayıcı mı?
        - Hata veya yanıltıcı bilgi var mı?
        
        Sadece "GOOD" veya "BAD" yaz. Tek kelime.
        """
        
        # Bu her seferinde $0.01 civarı maliyet!
        response = self.inference.infer(
            prompt=prompt,
            model="gpt-3.5-turbo",
            temperature=0
        )
        
        evaluation = response.content.strip().upper()
        return evaluation == "GOOD", evaluation
    
    def evaluate_batch(self, qa_pairs: List[Dict]) -> List[Dict]:
        """
        BATCH değerlendirme - EKONOMİK YÖNTEM!
        
        100 pair'i tek seferde değerlendirir.
        Maliyet: 100 pair için $0.02 (tek tek $1.00 yerine!)
        """
        
        # Örnek batch data:
        # [
        #   {"id": 1, "q": "Python nedir?", "a": "Python bir programlama dilidir..."},
        #   {"id": 2, "q": "For loop nasıl?", "a": "For loop şöyle: for i in range(10):..."},
        #   ... 98 tane daha
        # ]
        
        batch_prompt = f"""
        Aşağıdaki soru-cevap çiftlerini değerlendir.
        Sadece GOOD olanların ID'lerini virgülle ayırarak yaz.
        
        Kriterler:
        - Cevap soruya uygun
        - Yeterli detay var
        - Hata yok
        
        DATA:
        """
        
        # Her pair'i formatla
        for pair in qa_pairs:
            batch_prompt += f"\nID:{pair['id']} Q:{pair['q'][:100]} A:{pair['a'][:200]}"
        
        batch_prompt += "\n\nGOOD IDs:"
        
        # Tek API call - 100 evaluation!
        response = self.inference.infer(
            prompt=batch_prompt,
            model="gpt-3.5-turbo",
            temperature=0,
            max_tokens=500
        )
        
        # Parse response: "1,5,12,45,67,89"
        try:
            good_ids = [int(id.strip()) for id in response.content.split(",")]
        except:
            good_ids = []
        
        # Mark good ones
        for pair in qa_pairs:
            pair['is_good'] = pair['id'] in good_ids
            pair['evaluated_by'] = 'llm_batch'
        
        return qa_pairs


class SmartCollector:
    """
    Akıllı collector - staged approach ile maliyet optimizasyonu
    """
    
    def __init__(self, inference_manager):
        self.inference = inference_manager
        self.evaluator = LLMEvaluator(inference_manager)
        
        # Aşamalı toplama
        self.stage = 1
        self.collected_count = 0
        self.learned_patterns = {
            "good_indicators": [],
            "bad_indicators": []
        }
        
        # Buffer
        self.pending_evaluation = []
        self.validated_dataset = []
    
    def collect(self, session_id: str, input_text: str, output_text: str, model: str, latency: float):
        """
        ÖRNEK SENARYO:
        
        Kullanıcı: "Python'da dosya nasıl okunur?"
        Bot: "Python'da dosya okumak için: with open('file.txt', 'r') as f: content = f.read()"
        """
        
        data_point = {
            "id": self.collected_count,
            "session_id": session_id,
            "q": input_text,
            "a": output_text,
            "model": model,
            "latency": latency
        }
        
        self.collected_count += 1
        
        # STAGE 1: İlk 1000 veri - Sadece basit kontrol
        if self.stage == 1:
            if self._basic_quality_check(output_text, latency):
                self.pending_evaluation.append(data_point)
                
            # 1000 veri toplandı mı?
            if self.collected_count >= 1000:
                print("STAGE 1 bitti! 1000 veri toplandı. STAGE 2'ye geçiyoruz...")
                self.stage = 2
                # İlk batch'i değerlendir
                self._evaluate_pending_batch()
        
        # STAGE 2: 1000-5000 arası - %10 sampling ile LLM
        elif self.stage == 2:
            # Önce basit kontrol
            if self._basic_quality_check(output_text, latency):
                # %10 şansla LLM'e gönder
                import random
                if random.random() < 0.1:  # %10
                    self.pending_evaluation.append(data_point)
                else:
                    # Öğrendiğimiz pattern'lere göre değerlendir
                    if self._check_learned_patterns(input_text, output_text):
                        data_point['is_good'] = True
                        data_point['evaluated_by'] = 'learned_pattern'
                        self.validated_dataset.append(data_point)
            
            # Her 100 veri'de batch evaluation
            if len(self.pending_evaluation) >= 100:
                self._evaluate_pending_batch()
            
            # 5000'e ulaştık mı?
            if self.collected_count >= 5000:
                print("STAGE 2 bitti! Pattern'ler öğrenildi. STAGE 3'e geçiyoruz...")
                self.stage = 3
                self._learn_patterns_from_evaluated()
        
        # STAGE 3: 5000+ - Sadece öğrenilmiş pattern'ler
        else:
            # Artık LLM'e gerek yok!
            if self._basic_quality_check(output_text, latency):
                if self._check_learned_patterns(input_text, output_text):
                    data_point['is_good'] = True
                    data_point['evaluated_by'] = 'learned_pattern_only'
                    self.validated_dataset.append(data_point)
                    print(f"✓ Veri #{self.collected_count} otomatik onaylandı (LLM'siz!)")
    
    def _basic_quality_check(self, output: str, latency: float) -> bool:
        """Basit kalite kontrolü"""
        if len(output) < 50:
            return False
        if latency > 2000:
            return False
        if any(err in output.lower() for err in ["error", "exception", "failed"]):
            return False
        return True
    
    def _evaluate_pending_batch(self):
        """Bekleyen veriyi batch olarak değerlendir"""
        if not self.pending_evaluation:
            return
            
        print(f"🤖 LLM'e {len(self.pending_evaluation)} veri gönderiliyor...")
        
        # LLM batch evaluation
        evaluated = self.evaluator.evaluate_batch(self.pending_evaluation)
        
        # Good olanları kaydet
        good_count = 0
        for item in evaluated:
            if item.get('is_good'):
                self.validated_dataset.append(item)
                good_count += 1
        
        print(f"✓ {good_count}/{len(evaluated)} veri onaylandı")
        
        # Maliyet hesabı
        cost = len(self.pending_evaluation) * 0.0002  # ~$0.02 per 100
        print(f"💰 Tahmini maliyet: ${cost:.4f}")
        
        self.pending_evaluation.clear()
    
    def _check_learned_patterns(self, input_text: str, output_text: str) -> bool:
        """
        Öğrenilmiş pattern'lere göre kontrol
        
        Örnek öğrenilmiş pattern'ler:
        - "nasıl" soruları -> kod örneği içermeli
        - "nedir" soruları -> açıklama içermeli
        - Kod içeren cevaplar -> ``` olmalı
        """
        
        # Good indicators
        if "nasıl" in input_text.lower() and "```" in output_text:
            return True
        if "nedir" in input_text.lower() and len(output_text) > 100:
            return True
        if "örnek" in input_text.lower() and ("```" in output_text or "örneğin" in output_text.lower()):
            return True
        
        # Bad indicators
        if "sorry" in output_text.lower():
            return False
        if len(output_text.split()) < 10:
            return False
        
        # Default
        return len(output_text) > 100
    
    def _learn_patterns_from_evaluated(self):
        """LLM'den onaylanan verilerden pattern öğren"""
        print("🧠 Pattern'ler öğreniliyor...")
        
        good_data = [d for d in self.validated_dataset if d.get('is_good')]
        
        # Basit pattern extraction
        for data in good_data[:100]:  # İlk 100 good data
            q = data['q'].lower()
            a = data['a']
            
            # Question patterns
            if "nasıl" in q and "```" in a:
                self.learned_patterns['good_indicators'].append("how_to_with_code")
            if "nedir" in q and len(a) > 150:
                self.learned_patterns['good_indicators'].append("what_is_detailed")
            if "örnek" in q and "```" in a:
                self.learned_patterns['good_indicators'].append("example_with_code")
        
        print(f"✓ {len(self.learned_patterns['good_indicators'])} pattern öğrenildi!")
    
    def get_stats(self):
        """İstatistikleri göster"""
        return {
            "stage": self.stage,
            "total_collected": self.collected_count,
            "validated": len(self.validated_dataset),
            "pending": len(self.pending_evaluation),
            "estimated_cost": {
                "stage1": 0,
                "stage2": (self.collected_count - 1000) * 0.1 * 0.0002 if self.stage >= 2 else 0,
                "stage3": 0
            }
        }


# KULLANIM ÖRNEĞİ:
"""
collector = SmartCollector(inference_manager)

# İlk 1000 veri - MALİYET: $0
for i in range(1000):
    collector.collect(
        session_id="sess_1",
        input_text="Python'da liste nasıl oluşturulur?",
        output_text="Python'da liste şöyle oluşturulur: my_list = [1, 2, 3]",
        model="gpt-3.5-turbo",
        latency=245
    )

# 1000-5000 arası - MALİYET: ~$0.80 (400 veri × $0.002)
# Sadece %10'u LLM'e gider

# 5000+ sonrası - MALİYET: $0
# Artık tamamen pattern-based, LLM'e gerek yok!

print(collector.get_stats())
# Output:
# {
#   "stage": 3,
#   "total_collected": 10000,
#   "validated": 7500,
#   "estimated_cost": {"total": "$0.80"}
# }
"""