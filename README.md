# CrashScope

Real-time traffic incident analysis system combining live data APIs, machine learning predictions, and AI-powered reporting for comprehensive accident assessment in the Netherlands.

## System Architecture

### Data Pipeline
- **Source**: Live traffic incidents from TomTom Traffic API
- **Coverage**: 16 regional zones across Netherlands
- **Enrichment**: Real-time weather data, geolocation reversal, temporal features
- **Processing**: Feature engineering with ML-based risk assessment
- **Output**: Interactive web dashboard with predictive analytics

### Machine Learning Models

Three classification models trained on 238,525 Dutch traffic accident records (2022-2024):

#### 1. Severity Predictor
- **Algorithm**: Logistic Regression
- **Classes**: Fatal, Injury, Property Damage
- **Features**: Delay time, weather conditions, road type, lighting, time period

#### 2. Accident Type Classifier
- **Algorithm**: Logistic Regression  
- **Classes**: Collision, Single-Vehicle, Pedestrian, Other
- **Features**: Number of parties, location type, weather, temporal factors

#### 3. Location Risk Assessor
- **Algorithm**: Random Forest (50 trees)
- **Classes**: Urban, Rural
- **Features**: Speed limit, built-up area indicator, road characteristics

### API Integration

#### TomTom Services
1. **Traffic Incidents API** (`v5/incidentDetails`)
   - Real-time accident data with geometry coordinates
   - Category filtering for accident-specific incidents
   - Bounding box queries for regional coverage

2. **Reverse Geocoding API** (`v2/reverseGeocode`)
   - Coordinate-to-address conversion
   - Street-level location resolution
   - Multilingual address formatting

3. **Maps SDK** (`v6.25.0`)
   - Interactive map visualization
   - Custom marker rendering
   - Dynamic viewport adjustment

#### Open-Meteo Weather API
- Current weather conditions at incident coordinates
- Temperature, precipitation, wind speed
- Weather code translation (Clear/Rainy/Foggy/Snowy)

#### OpenRouter AI API
- **Model**: NVIDIA Nemotron Nano 9B v2 (free tier)
- Generates concise predictive incident reports
- Contextual analysis combining ML predictions and live data
- Markdown-formatted output (80 words max)

## Technical Implementation

### Backend (`app.py`)
- **Framework**: Flask 3.1.2 with CORS support and RESTful API with single endpoint

### Frontend (`static/index.html`)
- **Mapping**: TomTom Maps SDK v6.25.0
- **Visualization**: Custom risk-colored markers (High/Medium/Low)
- **Rendering**: Markdown parsing with marked.js
- **UI**: Responsive gradient design with modal detail views

## Configuration

Required environment variables (`.env`):
```bash
TOMTOM_API_KEY=<your_tomtom_api_key>
OPENROUTER_API_KEY=<your_openrouter_api_key>
```

## Data Source

**Training Dataset**: Dutch Road Accidents (RWS) 2022-2024  
**Provider**: European Data Portal  
**Format**: WFS Entity `verkeersongevallen_nederland:ongevallen_2022_2024`  
**Records**: 382,421 raw → 238,525 processed  
**Features**: 40 attributes including severity, type, location, weather, temporal data

## Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

Server runs on `http://localhost:5001` with debug mode enabled.

## Model Performance

| Model | Algorithm | Training Samples | Test Samples | Accuracy |
|-------|-----------|-----------------|--------------|----------|
| Severity | Logistic Regression | 190,829 | 47,696 | 100% |
| Accident Type | Logistic Regression | 190,829 | 47,696 | 100% |
| Location Risk | Random Forest | 190,829 | 47,696 | 100% |
