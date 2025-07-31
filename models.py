from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Initialize the SQLAlchemy object. It will be linked to the app in app.py.
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=True) # Made nullable as per auth_routes
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Preferences (as used in trip_routes)
    travel_style = db.Column(db.String(50), default='balanced')
    preferred_activities = db.Column(db.Text, nullable=True) # Stored as JSON string
    interests = db.Column(db.Text, nullable=True) # Stored as JSON string

    trips = db.relationship("Trip", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

    def get_preferred_activities(self):
        return json.loads(self.preferred_activities) if self.preferred_activities else []

    def get_interests(self):
        return json.loads(self.interests) if self.interests else []

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

class Trip(db.Model):
    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Merged fields from different versions
    title = db.Column(db.String(150), nullable=False)
    destination_city = db.Column(db.String(100), nullable=False)
    destination_country = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False) # In days

    status = db.Column(db.String(50), default='planned') # e.g., planned, active, completed
    travel_style = db.Column(db.String(50), nullable=True)
    interests = db.Column(db.Text, nullable=True) # JSON string

    budget_amount = db.Column(db.Float, nullable=True)
    budget_currency = db.Column(db.String(10), default='USD')

    itinerary_data = db.Column(db.Text, nullable=True) # Stored as JSON string
    weather_data = db.Column(db.Text, nullable=True) # Stored as JSON string

    ai_generated = db.Column(db.Boolean, default=False)
    generation_model = db.Column(db.String(50), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_interests(self):
        return json.loads(self.interests) if self.interests else []

    def set_itinerary_data(self, data):
        self.itinerary_data = json.dumps(data)

    def set_weather_data(self, data):
        self.weather_data = json.dumps(data)
        
    def to_dict(self, include_detailed=False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "destination_city": self.destination_city,
            "destination_country": self.destination_country,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "duration": self.duration,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }
        if include_detailed:
            data.update({
                "latitude": self.latitude,
                "longitude": self.longitude,
                "travel_style": self.travel_style,
                "interests": self.get_interests(),
                "budget": {"amount": self.budget_amount, "currency": self.budget_currency},
                "itinerary": json.loads(self.itinerary_data) if self.itinerary_data else None,
                "weather": json.loads(self.weather_data) if self.weather_data else None,
                "ai_generated": self.ai_generated,
                "generation_model": self.generation_model
            })
        return data
