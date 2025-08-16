import time
from typing import Dict
from transformers import pipeline


class EmotionAnalyzer:
    def __init__(self):
        self.model = None
        
    async def load_model(self):
        if self.model is None:
            self.model = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
    
    async def analyze(self, text: str) -> Dict:
        start_time = time.time()
        
        if self.model is None:
            await self.load_model()
        
        results = self.model(text)[0]
        
        emotions = {}
        for result in results:
            emotions[result['label']] = round(result['score'], 4)
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "emotions": emotions,
            "processing_time_ms": processing_time
        }