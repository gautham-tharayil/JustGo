from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)

# Enhanced CORS configuration
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], 
     methods=["GET", "POST", "PUT", "DELETE"], 
     allow_headers=["Content-Type", "Authorization"])

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "travel_planner.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Create tables and add default users
with app.app_context():
    db.create_all()
    
    # Add multiple test users
    test_users = [
        {"email": "admin@travel.com", "password": "admin123"},
        {"email": "user@demo.com", "password": "password"},
        {"email": "john@example.com", "password": "john123"},
    ]
    
    for user_data in test_users:
        if not User.query.filter_by(email=user_data["email"]).first():
            user = User(email=user_data["email"], password=user_data["password"])
            db.session.add(user)
    
    db.session.commit()
    print("✅ Test users created:")
    print("   admin@travel.com / admin123")
    print("   user@demo.com / password") 
    print("   john@example.com / john123")
    print(f"✅ Database initialized at: sqlite:///{DB_PATH}")

@app.route('/login', methods=['POST'])
def login():
    try:
        # Check if request has JSON data
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            return jsonify({
                "message": "Login successful", 
                "user": {"id": user.id, "email": user.email}
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/dashboard', methods=['GET'])
def dashboard():
    try:
        return jsonify({
            "welcome": "Welcome to your Travel Planner Dashboard!",
            "user_stats": {
                "total_trips": 5,
                "upcoming_trips": 2,
                "completed_trips": 3,
                "favorite_destinations": ["Paris", "Tokyo", "New York"]
            },
            "recent_trips": [
                {
                    "id": 1,
                    "destination": "Paris, France",
                    "date": "2024-12-15",
                    "duration": "7 days",
                    "status": "upcoming",
                    "image": "🇫🇷"
                },
                {
                    "id": 2,
                    "destination": "Tokyo, Japan", 
                    "date": "2024-11-20",
                    "duration": "10 days",
                    "status": "completed",
                    "image": "🇯🇵"
                },
                {
                    "id": 3,
                    "destination": "New York, USA",
                    "date": "2025-01-10", 
                    "duration": "5 days",
                    "status": "upcoming",
                    "image": "🇺🇸"
                }
            ],
            "quick_actions": [
                "Plan New Trip",
                "Check Weather", 
                "Browse Destinations",
                "View Saved Places"
            ],
            "weather_info": {
                "current_location": "Your Location",
                "temperature": "22°C",
                "condition": "Sunny",
                "humidity": "65%"
            }
        }), 200
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/trips', methods=['GET'])
def get_trips():
    try:
        trips = [
            {
                "id": 1,
                "destination": "Paris, France",
                "date": "2024-12-15",
                "duration": "7 days",
                "status": "upcoming",
                "budget": "$2,500",
                "activities": ["Eiffel Tower", "Louvre Museum", "Seine River Cruise"],
                "image": "🇫🇷"
            },
            {
                "id": 2,
                "destination": "Tokyo, Japan",
                "date": "2024-11-20", 
                "duration": "10 days",
                "status": "completed",
                "budget": "$3,200",
                "activities": ["Tokyo Tower", "Shibuya Crossing", "Mount Fuji"],
                "image": "🇯🇵"
            },
            {
                "id": 3,
                "destination": "New York, USA",
                "date": "2025-01-10",
                "duration": "5 days", 
                "status": "upcoming",
                "budget": "$1,800",
                "activities": ["Central Park", "Times Square", "Statue of Liberty"],
                "image": "🇺🇸"
            },
            {
                "id": 4,
                "destination": "London, UK",
                "date": "2024-10-05",
                "duration": "6 days",
                "status": "completed", 
                "budget": "$2,100",
                "activities": ["Big Ben", "Tower Bridge", "British Museum"],
                "image": "🇬🇧"
            }
        ]
        return jsonify({"trips": trips}), 200
    except Exception as e:
        print(f"Trips error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/destinations', methods=['GET'])
def get_destinations():
    try:
        destinations = [
            {
                "id": 1,
                "name": "Bali, Indonesia",
                "description": "Tropical paradise with stunning beaches and temples",
                "rating": 4.8,
                "price_range": "$50-150/day",
                "best_time": "Apr-Oct",
                "image": "🏝️"
            },
            {
                "id": 2,
                "name": "Rome, Italy", 
                "description": "Historic city with ancient ruins and amazing cuisine",
                "rating": 4.7,
                "price_range": "$80-200/day",
                "best_time": "Apr-Jun, Sep-Oct",
                "image": "🏛️"
            },
            {
                "id": 3,
                "name": "Dubai, UAE",
                "description": "Modern luxury destination with world-class shopping",
                "rating": 4.6,
                "price_range": "$100-300/day", 
                "best_time": "Nov-Mar",
                "image": "🏙️"
            },
            {
                "id": 4,
                "name": "Iceland",
                "description": "Natural wonders with glaciers, geysers, and northern lights",
                "rating": 4.9,
                "price_range": "$120-250/day",
                "best_time": "Jun-Aug, Sep-Mar",
                "image": "🏔️"
            }
        ]
        return jsonify({"destinations": destinations}), 200
    except Exception as e:
        print(f"Destinations error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/weather/<city>', methods=['GET'])
def get_weather(city):
    try:
        # Mock weather data
        weather_data = {
            "Paris": {"temp": "18°C", "condition": "Cloudy", "humidity": "70%"},
            "Tokyo": {"temp": "25°C", "condition": "Sunny", "humidity": "60%"},
            "New York": {"temp": "22°C", "condition": "Partly Cloudy", "humidity": "65%"},
            "London": {"temp": "15°C", "condition": "Rainy", "humidity": "80%"},
            "Bali": {"temp": "30°C", "condition": "Sunny", "humidity": "75%"},
            "Rome": {"temp": "26°C", "condition": "Clear", "humidity": "55%"},
            "Dubai": {"temp": "35°C", "condition": "Hot", "humidity": "40%"},
            "Iceland": {"temp": "8°C", "condition": "Snowy", "humidity": "85%"}
        }
        
        weather = weather_data.get(city, {"temp": "N/A", "condition": "Unknown", "humidity": "N/A"})
        
        return jsonify({
            "city": city,
            "weather": weather,
            "forecast": [
                {"day": "Today", "temp": weather["temp"], "condition": weather["condition"]},
                {"day": "Tomorrow", "temp": "20°C", "condition": "Sunny"},
                {"day": "Day 3", "temp": "19°C", "condition": "Cloudy"}
            ]
        }), 200
    except Exception as e:
        print(f"Weather error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/')
def home():
    return jsonify({"message": "Flask backend running successfully!"}), 200

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "Server is running"}), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    print("🚀 Starting Flask server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🔧 Debug mode: ON")
    app.run(debug=True, host='0.0.0.0', port=5000)