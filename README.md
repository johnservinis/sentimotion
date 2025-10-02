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
docker pull johnserv/sentimotion:latest
docker run -p 8010:8010 johnserv/sentimotion:latest
```

#### Option 2: Build Locally
1. Build the image:
```bash
docker build -t sentimotion .
```

2. Run the container:
```bash
docker run -p 8010:8010 sentimotion
```

#### Automated Deployment
This project automatically builds and pushes Docker images to Docker Hub on every push to the main branch using GitHub Actions. Images are available at:
- `johnserv/sentimotion:latest` (latest main branch)
- `johnserv/sentimotion:main-<commit-sha>` (specific commits)

## Production Deployment (Google Cloud Run)

### Quick Deploy
For production deployment with auto-scaling and cost optimization:

```bash
# Deploy directly to Cloud Run
gcloud run deploy sentimotion \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --max-instances 100
```

### GitHub Actions Deployment
Automated deployment to Cloud Run is configured via GitHub Actions. To set up:

1. **Create Google Cloud Project**
   ```bash
   gcloud projects create your-project-id
   gcloud config set project your-project-id
   ```

2. **Enable Required APIs**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

3. **Create Service Account**
   ```bash
   gcloud iam service-accounts create github-actions \
     --display-name="GitHub Actions"
   
   gcloud projects add-iam-policy-binding your-project-id \
     --member="serviceAccount:github-actions@your-project-id.iam.gserviceaccount.com" \
     --role="roles/run.admin"
   
   gcloud projects add-iam-policy-binding your-project-id \
     --member="serviceAccount:github-actions@your-project-id.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   
   gcloud iam service-accounts keys create key.json \
     --iam-account=github-actions@your-project-id.iam.gserviceaccount.com
   ```

4. **Configure GitHub Secrets**
   - `GCP_PROJECT_ID`: Your Google Cloud project ID
   - `GCP_SA_KEY`: Contents of the `key.json` file

### Production Features
- **Auto-scaling**: 0-100 instances based on demand
- **Cost optimization**: Scales to zero when idle
- **Health checks**: Enhanced monitoring and readiness checks
- **Graceful shutdown**: Proper signal handling for zero-downtime deployments
- **Logging**: Structured logging for production monitoring

### Expected Costs
- **Light usage** (1K requests/day): ~$5-10/month
- **Medium usage** (10K requests/day): ~$20-40/month  
- **Heavy usage** (100K requests/day): ~$100-200/month
- **Peak handling**: Automatically scales to handle traffic spikes up to 1000 concurrent requests

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