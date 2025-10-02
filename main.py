import time
import os
import signal
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models.emotion_analyzer import EmotionAnalyzer
from models.sentiment_analyzer import SentimentAnalyzer


# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global analyzers
emotion_analyzer = None
sentiment_analyzer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global emotion_analyzer, sentiment_analyzer
    logger.info("Loading ML models...")
    
    emotion_analyzer = EmotionAnalyzer()
    sentiment_analyzer = SentimentAnalyzer()
    
    await emotion_analyzer.load_model()
    await sentiment_analyzer.load_model()
    
    logger.info("ML models loaded successfully")
    yield
    # Shutdown
    logger.info("Shutting down gracefully")

app = FastAPI(
    title="Emotion & Sentiment Analyzer",
    description="Microservice for analyzing emotions and sentiment in text",
    version="1.0.0",
    lifespan=lifespan
)


class TextInput(BaseModel):
    text: str


class EmotionResponse(BaseModel):
    text: str
    emotions: dict
    telemetry: dict


class SentimentResponse(BaseModel):
    text: str
    sentiment: dict
    telemetry: dict


class CombinedResponse(BaseModel):
    emotions: dict
    sentiment: dict
    telemetry: dict




@app.get("/health")
async def health_check():
    # Enhanced health check for Cloud Run
    models_loaded = emotion_analyzer is not None and sentiment_analyzer is not None
    return {
        "status": "healthy" if models_loaded else "loading",
        "service": "emotion-sentiment-analyzer",
        "models_loaded": models_loaded,
        "version": "1.0.0"
    }


@app.post("/emotion", response_model=EmotionResponse)
async def analyze_emotion(input_data: TextInput):
    try:
        result = await emotion_analyzer.analyze(input_data.text)
        
        return EmotionResponse(
            text=input_data.text,
            emotions=result["emotions"],
            telemetry={
                "emotion_processing_time_ms": result["processing_time_ms"]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing emotion: {str(e)}")


@app.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(input_data: TextInput):
    try:
        result = await sentiment_analyzer.analyze(input_data.text)
        
        return SentimentResponse(
            text=input_data.text,
            sentiment=result["sentiment"],
            telemetry={
                "sentiment_processing_time_ms": result["processing_time_ms"]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")


@app.post("/analyze", response_model=CombinedResponse)
async def analyze_combined(input_data: TextInput):
    try:
        start_time = time.time()
        
        emotion_result = await emotion_analyzer.analyze(input_data.text)
        sentiment_result = await sentiment_analyzer.analyze(input_data.text)
        
        total_time = round((time.time() - start_time) * 1000, 2)
        
        return CombinedResponse(
            emotions=emotion_result["emotions"],
            sentiment=sentiment_result["sentiment"],
            telemetry={
                "emotion_processing_time_ms": emotion_result["processing_time_ms"],
                "sentiment_processing_time_ms": sentiment_result["processing_time_ms"],
                "total_processing_time_ms": total_time
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in combined analysis: {str(e)}")


# Graceful shutdown handler
def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8010))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        access_log=True,
        log_level="info"
    )