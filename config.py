import os
from datetime import timedelta

class Config:
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/travel.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    GOOGLE_PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')  
    
    
    RATELIMIT_STORAGE_URL = 'memory://'
    
    
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  
    UPLOAD_FOLDER = 'uploads'
    
    
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    
    
    DEFAULT_AI_MODEL = 'gpt-3.5-turbo'
    MAX_ITINERARY_DAYS = 30
    MIN_ITINERARY_DAYS = 1