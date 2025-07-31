# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    profile_picture = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    nationality = db.Column(db.String(50))
    
    # Travel preferences stored as JSON strings
    interests = db.Column(db.Text)  # JSON array of interests
    budget_min = db.Column(db.Float, default=0)
    budget_max = db.Column(db.Float, default=5000)
    preferred_activities = db.Column(db.Text)  # JSON array
    travel_style = db.Column(db.String(20), default='mid-range')
    accommodation_preference = db.Column(db.String(20), default='any')
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    trips = db.relationship('Trip', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_interests(self):
        """Get interests as Python list"""
        try:
            return json.loads(self.interests) if self.interests else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_interests(self, interests_list):
        """Set interests from Python list"""
        self.interests = json.dumps(interests_list) if interests_list else None
    
    def get_preferred_activities(self):
        """Get preferred activities as Python list"""
        try:
            return json.loads(self.preferred_activities) if self.preferred_activities else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_preferred_activities(self, activities_list):
        """Set preferred activities from Python list"""
        self.preferred_activities = json.dumps(activities_list) if activities_list else None
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email if include_sensitive else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_picture': self.profile_picture,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'nationality': self.nationality,
            'interests': self.get_interests(),
            'budget_range': {
                'min': self.budget_min,
                'max': self.budget_max
            },
            'preferred_activities': self.get_preferred_activities(),
            'travel_style': self.travel_style,
            'accommodation_preference': self.accommodation_preference,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data['email'] = self.email
            
        return data

class Trip(db.Model):
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Trip basic information
    title = db.Column(db.String(200))
    destination_city = db.Column(db.String(100), nullable=False)
    destination_country = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Trip details
    duration = db.Column(db.Integer, nullable=False)  # Number of days
    budget_amount = db.Column(db.Float, nullable=False)
    budget_currency = db.Column(db.String(10), default='USD')
    
    # Trip preferences
    interests = db.Column(db.Text)  # JSON array of selected interests
    travel_style = db.Column(db.String(20))  # Override user's default style
    
    # Generated itinerary data
    itinerary_data = db.Column(db.Text)  # JSON object containing day-wise plan
    ai_generated = db.Column(db.Boolean, default=False)
    generation_model = db.Column(db.String(50))  # Which AI model was used
    
    # Trip dates
    start_date = db.Column(db.Date, index=True)
    end_date = db.Column(db.Date, index=True)
    
    # Trip status and metadata
    status = db.Column(db.String(20), default='draft', index=True)  # draft, confirmed, completed, cancelled
    is_public = db.Column(db.Boolean, default=False)
    is_favorite = db.Column(db.Boolean, default=False)
    
    # Additional metadata
    notes = db.Column(db.Text)
    tags = db.Column(db.Text)  # JSON array of custom tags
    weather_data = db.Column(db.Text)  # JSON weather information
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_interests(self):
        """Get interests as Python list"""
        try:
            return json.loads(self.interests) if self.interests else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_interests(self, interests_list):
        """Set interests from Python list"""
        self.interests = json.dumps(interests_list) if interests_list else None
    
    def get_itinerary_data(self):
        """Get itinerary data as Python object"""
        try:
            return json.loads(self.itinerary_data) if self.itinerary_data else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_itinerary_data(self, data):
        """Set itinerary data from Python object"""
        self.itinerary_data = json.dumps(data) if data else None
    
    def get_tags(self):
        """Get tags as Python list"""
        try:
            return json.loads(self.tags) if self.tags else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_tags(self, tags_list):
        """Set tags from Python list"""
        self.tags = json.dumps(tags_list) if tags_list else None
    
    def get_weather_data(self):
        """Get weather data as Python object"""
        try:
            return json.loads(self.weather_data) if self.weather_data else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_weather_data(self, data):
        """Set weather data from Python object"""
        self.weather_data = json.dumps(data) if data else None
    
    def generate_title(self):
        """Auto-generate trip title if not set"""
        if not self.title:
            self.title = f"{self.duration}-day trip to {self.destination_city}"
    
    def to_dict(self, include_detailed=True):
        """Convert trip to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'destination': {
                'city': self.destination_city,
                'country': self.destination_country,
                'coordinates': {
                    'latitude': self.latitude,
                    'longitude': self.longitude
                } if self.latitude and self.longitude else None
            },
            'duration': self.duration,
            'budget': {
                'amount': self.budget_amount,
                'currency': self.budget_currency
            },
            'interests': self.get_interests(),
            'travel_style': self.travel_style,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'is_public': self.is_public,
            'is_favorite': self.is_favorite,
            'ai_generated': self.ai_generated,
            'generation_model': self.generation_model,
            'tags': self.get_tags(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_detailed:
            data.update({
                'itinerary_data': self.get_itinerary_data(),
                'notes': self.notes,
                'weather_data': self.get_weather_data()
            })
        
        return data

class TravelTip(db.Model):
    __tablename__ = 'travel_tips'
    
    id = db.Column(db.Integer, primary_key=True)
    destination_city = db.Column(db.String(100), nullable=False, index=True)
    destination_country = db.Column(db.String(100), nullable=False, index=True)
    
    # Tip information
    category = db.Column(db.String(50), nullable=False, index=True)  # weather, customs, transportation, safety, etc.
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # Seasonal and contextual relevance
    applicable_months = db.Column(db.Text)  # JSON array of month numbers (1-12)
    applicable_seasons = db.Column(db.Text)  # JSON array of seasons
    
    # Priority and metadata
    priority = db.Column(db.Integer, default=1)  # 1-5, higher is more important
    is_active = db.Column(db.Boolean, default=True)
    source = db.Column(db.String(100))  # Source of the tip
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_applicable_months(self):
        """Get applicable months as Python list"""
        try:
            return json.loads(self.applicable_months) if self.applicable_months else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_applicable_months(self, months_list):
        """Set applicable months from Python list"""
        self.applicable_months = json.dumps(months_list) if months_list else None
    
    def get_applicable_seasons(self):
        """Get applicable seasons as Python list"""
        try:
            return json.loads(self.applicable_seasons) if self.applicable_seasons else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_applicable_seasons(self, seasons_list):
        """Set applicable seasons from Python list"""
        self.applicable_seasons = json.dumps(seasons_list) if seasons_list else None
    
    def to_dict(self):
        """Convert travel tip to dictionary"""
        return {
            'id': self.id,
            'destination': {
                'city': self.destination_city,
                'country': self.destination_country
            },
            'category': self.category,
            'title': self.title,
            'content': self.content,
            'applicable_months': self.get_applicable_months(),
            'applicable_seasons': self.get_applicable_seasons(),
            'priority': self.priority,
            'is_active': self.is_active,
            'source': self.source,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Database indexes for performance
db.Index('idx_user_email_username', User.email, User.username)
db.Index('idx_trip_user_status', Trip.user_id, Trip.status)
db.Index('idx_trip_destination', Trip.destination_city, Trip.destination_country)
db.Index('idx_tip_destination_category', TravelTip.destination_city, TravelTip.destination_country, TravelTip.category)