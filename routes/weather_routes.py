# routes/weather_routes.py
from flask import Blueprint, request, jsonify
import requests
import requests_cache
from retry_requests import retry
import openmeteo_requests
import pandas as pd
import os

weather_bp = Blueprint('weather', __name__)

# Use your geocoding API key (from environment or config)
GEOCODING_API_KEY = os.getenv("GEOCODING_API_KEY")

def get_coordinates(city):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={GEOCODING_API_KEY}"
    res = requests.get(url).json()
    if res["status"] == "OK":
        loc = res["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    else:
        raise ValueError("City not found")

def get_weather(city):
    lat, lon = get_coordinates(city)

    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    hourly = response.Hourly()
    hourly_temp = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ).astype(str).tolist(),
        "temperature_2m": hourly_temp.tolist()
    }

    return hourly_data

# Flask route
@weather_bp.route('/forecast', methods=['GET'])
def forecast():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City query param is required"}), 400
    try:
        weather = get_weather(city)
        return jsonify({"city": city, "data": weather})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
