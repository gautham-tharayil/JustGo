from flask import Blueprint, request, jsonify
import requests
import requests_cache
from retry_requests import retry
import openmeteo_requests
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta


load_dotenv()

weather_bp = Blueprint("weather", __name__)
GEOCODING_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_coordinates(city, country=None):
    """Fetch latitude & longitude from Google Maps API."""
    if not GEOCODING_API_KEY:
        raise ValueError("GOOGLE_MAPS_API_KEY not set in environment")

    query = f"{city},{country}" if country else city
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={query}&key={GEOCODING_API_KEY}"
    res = requests.get(url).json()

    if res.get("status") == "OK":
        loc = res["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    else:
        raise ValueError(f"City not found: {res.get('status')}")

def get_weather_data(lat, lon, start_date=None, duration=3):
    """Fetch weather data for given lat/lon, optionally by date range."""
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
        "timezone": "auto",
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    hourly = response.Hourly()
    hourly_temp = hourly.Variables(0).ValuesAsNumpy()

    hourly_dates = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left",
    )

    weather_df = pd.DataFrame({"date": hourly_dates, "temperature_2m": hourly_temp})

    if start_date:
        start_date = pd.to_datetime(start_date)
        end_date = start_date + timedelta(days=duration)
        mask = (weather_df["date"] >= start_date) & (weather_df["date"] <= end_date)
        weather_df = weather_df.loc[mask]

    return weather_df.to_dict(orient="list")

@weather_bp.route("/forecast", methods=["GET"])
def forecast():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City query param is required"}), 400
    try:
        lat, lon = get_coordinates(city)
        weather = get_weather_data(lat, lon, datetime.utcnow(), 3)
        return jsonify({"city": city, "data": weather})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


__all__ = ["get_coordinates", "get_weather_data", "weather_bp"]
