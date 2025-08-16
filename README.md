# Emotion & Sentiment Analyzer

A FastAPI microservice that provides emotion analysis and sentiment analysis for text inputs using state-of-the-art Hugging Face models.

## Features

- **Emotion Analysis**: Uses `j-hartmann/emotion-english-distilroberta-base` to classify text into 7 emotions (anger, disgust, fear, joy, neutral, sadness, surprise)
- **Sentiment Analysis**: Uses `ProsusAI/finbert` for financial sentiment analysis (positive, negative, neutral)
- **Combined Analysis**: Single endpoint for both emotion and sentiment analysis
- **Telemetry**: Processing time tracking for performance monitoring
- **JSON API**: RESTful API with Pydantic validation

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service:
```bash
python main.py
```

The API will be available at `http://localhost:8010`

### Docker

#### Option 1: Use Pre-built Image from Docker Hub
```bash
docker pull yourusername/il-emotion-and-sentiment-analyser:latest
docker run -p 8010:8010 yourusername/il-emotion-and-sentiment-analyser:latest
```

#### Option 2: Build Locally
1. Build the image:
```bash
docker build -t il-emotion-and-sentiment-analyser .
```

2. Run the container:
```bash
docker run -p 8010:8010 il-emotion-and-sentiment-analyser
```

#### Automated Deployment
This project automatically builds and pushes Docker images to Docker Hub on every push to the main branch using GitHub Actions. Images are available at:
- `yourusername/il-emotion-and-sentiment-analyser:latest` (latest main branch)
- `yourusername/il-emotion-and-sentiment-analyser:main-<commit-sha>` (specific commits)

## API Endpoints

### Health Check
```
GET /health
```

### Emotion Analysis Only
```
POST /emotion
Content-Type: application/json

{
  "text": "I love this amazing product!"
}
```

Response:
```json
{
  "text": "I love this amazing product!",
  "emotions": {
    "joy": 0.8765,
    "anger": 0.0234,
    "disgust": 0.0123,
    "fear": 0.0145,
    "neutral": 0.0234,
    "sadness": 0.0234,
    "surprise": 0.0265
  },
  "telemetry": {
    "emotion_processing_time_ms": 245.67
  }
}
```

### Sentiment Analysis Only
```
POST /sentiment
Content-Type: application/json

{
  "text": "The stock prices are rising significantly"
}
```

Response:
```json
{
  "text": "The stock prices are rising significantly",
  "sentiment": {
    "label": "positive",
    "confidence": 0.9234
  },
  "telemetry": {
    "sentiment_processing_time_ms": 189.45
  }
}
```

### Combined Analysis
```
POST /analyze
Content-Type: application/json

{
  "text": "I'm really excited about the market growth!"
}
```

Response:
```json
{
  "text": "I'm really excited about the market growth!",
  "emotions": {
    "joy": 0.8234,
    "anger": 0.0123,
    "disgust": 0.0234,
    "fear": 0.0234,
    "neutral": 0.0456,
    "sadness": 0.0234,
    "surprise": 0.0485
  },
  "sentiment": {
    "label": "positive",
    "confidence": 0.8945
  },
  "telemetry": {
    "emotion_processing_time_ms": 234.56,
    "sentiment_processing_time_ms": 178.23,
    "total_processing_time_ms": 412.79
  }
}
```

## Interactive API Documentation

Once the service is running, visit:
- Swagger UI: `http://localhost:8010/docs`
- ReDoc: `http://localhost:8010/redoc`

## Models Used

- **Emotion**: [j-hartmann/emotion-english-distilroberta-base](https://huggingface.co/j-hartmann/emotion-english-distilroberta-base)
- **Sentiment**: [ProsusAI/finbert](https://huggingface.co/ProsusAI/finbert)

## Performance Notes

- Models are loaded once at startup for optimal performance
- First request may take longer due to model initialization
- Subsequent requests are faster due to model caching
- Processing times are included in telemetry for monitoring