# CrashScope Web Application

Modern web interface for live traffic incident analysis and ML-based crash prediction in the Netherlands.

## Features

- **Live Incident Fetching**: Real-time traffic accident data from TomTom API
- **Interactive Map**: Netherlands map with OpenStreetMap showing incident locations
- **ML Predictions**: Machine learning models predict severity, accident type, and location risk
- **Rich Details**: Comprehensive incident reports including:
  - Location and coordinates
  - Risk assessment (High/Medium/Low)
  - Weather conditions
  - Road infrastructure
  - ML model predictions with confidence scores

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Ensure your `.env` file contains your TomTom API key:

```
TOMTOM_API_KEY=your_api_key_here
```

### 3. Start the Server

```bash
python app.py
```

The server will start at `http://localhost:5001`

### 4. Open in Browser

Navigate to `http://localhost:5001` in your web browser

## Usage

1. **Click "Look for Live Accidents"** button to fetch current incidents
2. **View incidents on map** - Each marker shows an incident location
3. **Click any marker** to open detailed incident report with:
   - Location information
   - Risk assessment
   - Weather conditions
   - ML predictions (severity, type, risk)
   - Confidence scores

## Architecture

### Backend (`app.py`)
- **Flask REST API** with CORS support
- **Endpoints**:
  - `GET /` - Serves the web interface
  - `GET /api/fetch-incidents` - Fetches live incidents with ML predictions
  - `GET /api/health` - Health check endpoint

### Frontend (`static/index.html`)
- **Leaflet.js** for interactive OpenStreetMap
- **Modern responsive UI** with gradient design
- **Real-time statistics** panel
- **Modal dialogs** for detailed incident reports

### ML Integration (`crashscope/utils/ml_predictor.py`)
- Loads trained models from `models/` directory
- Predicts:
  - **Severity**: Accident severity level
  - **Type**: Accident type classification
  - **Location Risk**: Area-specific risk assessment

## API Response Format

```json
{
  "success": true,
  "count": 20,
  "incidents": [
    {
      "id": "incident_52.1234_5.6789",
      "coordinates": {
        "lat": 52.1234,
        "lon": 5.6789
      },
      "location": "Utrecht",
      "risk_score": 7,
      "risk_level": "High",
      "road_type": "primary",
      "speed_limit": 50,
      "weather": "Droog",
      "temperature": 2.5,
      "time_period": "Night",
      "is_night": true,
      "parties_involved": 2,
      "predictions": {
        "severity": "Severe",
        "severity_confidence": 0.85,
        "accident_type": "Head-on collision",
        "type_confidence": 0.78
      }
    }
  ]
}
```

## Technologies

- **Backend**: Flask, Flask-CORS
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Mapping**: Leaflet.js + OpenStreetMap
- **ML**: scikit-learn, pandas, numpy
- **APIs**: TomTom Traffic API, Open-Meteo Weather API, OpenStreetMap Overpass API

## Development

The application runs in debug mode by default with auto-reload enabled. Any changes to `app.py` will automatically restart the server.

### Port Configuration

Default port is `5001`. To change:

```python
app.run(debug=True, host='0.0.0.0', port=YOUR_PORT)
```

## Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

## Notes

- ML models are loaded from the `models/` directory at startup
- If models are not found, predictions will return `None` values
- The application scans 16 regions across Netherlands for complete coverage
- Duplicate incidents are automatically filtered by coordinates
