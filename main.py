import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models.emotion_analyzer import EmotionAnalyzer
from models.sentiment_analyzer import SentimentAnalyzer


app = FastAPI(
    title="PulseChamp Emotion & Sentiment Analyzer",
    description="Microservice for analyzing emotions and sentiment in text",
    version="1.0.0"
)

emotion_analyzer = EmotionAnalyzer()
sentiment_analyzer = SentimentAnalyzer()


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
    text: str
    emotions: dict
    sentiment: dict
    telemetry: dict


@app.on_event("startup")
async def startup_event():
    await emotion_analyzer.load_model()
    await sentiment_analyzer.load_model()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "emotion-sentiment-analyzer"}


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
            text=input_data.text,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)