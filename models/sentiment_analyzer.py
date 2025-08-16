import time
from typing import Dict
from transformers import pipeline


class SentimentAnalyzer:
    def __init__(self):
        self.model = None
        
    async def load_model(self):
        if self.model is None:
            self.model = pipeline(
                "text-classification",
                model="ProsusAI/finbert",
                return_all_scores=True
            )
    
    async def analyze(self, text: str) -> Dict:
        start_time = time.time()
        
        if self.model is None:
            await self.load_model()
        
        results = self.model(text)[0]
        
        # Get the highest scoring sentiment
        best_result = max(results, key=lambda x: x['score'])
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "sentiment": {
                "label": best_result['label'],
                "confidence": round(best_result['score'], 4)
            },
            "processing_time_ms": processing_time
        }