# CrashScope

CrashScope uses a machine-learning model trained on car accident data. It pulls live incidents from the TomTom API, adds weather data, and predicts the size and impact of each crash. Useful for traffic services, insurance teams, or emergency planners.

### Find outs so far ...

##### Data
We can train the machine learning based on the data in format WFS for entity `verkeersongevallen_nederland:ongevallen_2022_2024`
[Road accidents Netherlands - Accidents 2020 - 2022 (RWS) from European data](https://data.europa.eu/data/datasets/i3qf48xk-czi1-04y7-0fgr-4dcd08qymmge?locale=en)

##### Live Accidents API
With TomTom API we can see live trafic 
[TomTom Traffic Incidents API](https://developer.tomtom.com/traffic-api/documentation/tomtom-maps/traffic-incidents/incident-details)

Sample curl request:
```bash
curl "https://api.tomtom.com/traffic/services/5/incidentDetails?key=<TomTomApiKey>&bbox=4.4,52.2,5.4,53.5&categoryFilter=1&timeValidityFilter=present"
```

Python code:
```python
def get_tomtom_accidents(key, bbox):
    url = (
        "https://api.tomtom.com/traffic/services/5/incidentDetails"
        f"?key={key}&bbox={bbox}&categoryFilter=1&timeValidityFilter=present"
    )
    return requests.get(url).json()

tomtom = get_tomtom_accidents(
    "<key>",
    "4.7,52.2,5.4,53.5"
)

print(tomtom)

```

##### Weather API

Sample code
```py
def get_live_weather(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&current=temperature_2m,precipitation,wind_speed_10m,weathercode"
    )
    return requests.get(url).json()

# example for first accident
ex_lat, ex_lon = accident_points[0]
weather_now = get_live_weather(ex_lat, ex_lon)
print(weather_now)
```
