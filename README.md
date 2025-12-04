# CrashScope

Real-time traffic incident analysis system combining live data APIs, machine learning predictions, and AI-powered reporting for  accident assessment in the Netherlands.

## System Architecture

<img width="2001" height="1324" alt="image" src="https://github.com/user-attachments/assets/1029d69c-f344-46ba-a9fe-0df5bdb435c7" />


### Data Pipeline & Workflow
1. **Live Data Ingestion**: TomTom Traffic API fetches real-time incidents in Netherlands
2. **Feature Engineering**: Extract temporal features (hour, weekend, rush hour), fetch weather data
3. **ML Prediction**: Pass features to trained models for severity, accident type, and location risk predictions
4. **AI Report Generation**: NVIDIA Nemotron Nano 9B generates contextual incident reports using ML predictions
5. **Web Visualization**: TomTom Maps SDK displays incidents with risk-colored markers and detailed modal views

### Machine Learning Models

Three classification models trained on 238,525 Dutch traffic accident records (2022-2024):

#### 1. Severity Predictor
- **Algorithm**: Logistic Regression
- **Test Accuracy**: 72.88%
- **Classes**: 3 levels - Fatal, Injury, Property Damage Only
- **Dataset**: 190,829 training samples, 47,696 test samples

#### 2. Accident Type Classifier
- **Algorithm**: Logistic Regression  
- **Test Accuracy**: 35.95%
- **Classes**: 10 categories - Animal, Single-vehicle, Side collision, Head-on, Parked vehicle, Rear-end, Loose object, Unknown, Fixed object, Pedestrian

#### 3. Location Risk Assessor
- **Algorithm**: Random Forest (50 trees)
- **Test Accuracy**: 93.26%
- **Classes**: 2 levels - Urban (Built-up area), Rural (Non-built-up area)

### API Integration

#### TomTom Services
1. **Traffic Incidents API**: Real-time accident data
2. **Reverse Geocoding API**: Street-level location resolution and coordinate-to-address conversion
3. **Maps SDK**: Interactive map visualization

#### Open-Meteo Weather API
Current weather conditions at incident coordinates with features Temperature, precipitation, wind speed

#### OpenRouter AI API
 NVIDIA Nemotron Nano 9B v2 (free tier) which Generates predictive incident reports


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

## Setup and Deployment

Install Dependencies
```bash
pip install -r requirements.txt
```

Run web server
```bash
python app.py
```
