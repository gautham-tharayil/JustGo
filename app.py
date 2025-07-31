import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# --- 1. App Initialization & Configuration ---
app = Flask(__name__)

# Apply CORS settings to allow requests from your React app.
# This configuration allows all API routes to be accessed.
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})

# Configure the database path.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "travel_planner.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# --- 2. Database Model Definition ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # In a real app, this should store a hashed password, not plain text.
    password = db.Column(db.String(120), nullable=False)


# --- 3. API Routes ---
# All routes now have the '/api' prefix to match the front-end requests.

@app.route('/api/login', methods=['POST'])
def login():
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        # SECURITY WARNING: This checks a plain text password!
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

@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    # This route now correctly matches the fetch call from the React Dashboard component.
    try:
        return jsonify({
            "welcome": "Welcome to your Travel Planner Dashboard!",
            "user_stats": {
                "total_trips": 5,
                "upcoming_trips": 2,
                "completed_trips": 3,
                "favorite_destinations": ["Paris", "Tokyo", "New York"]
            },
            # ... other dashboard data ...
        }), 200
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# --- 4. Database Creation and Seeding ---
# This block runs once when the app starts to set up the database.
with app.app_context():
    db.create_all()
    
    test_users = [
        {"email": "admin@travel.com", "password": "admin123"},
        {"email": "user@demo.com", "password": "password"},
    ]
    
    for user_data in test_users:
        if not User.query.filter_by(email=user_data["email"]).first():
            user = User(email=user_data["email"], password=user_data["password"])
            db.session.add(user)
    
    db.session.commit()
    print(f"✅ Database initialized at: {DB_PATH}")


# --- 5. App Runner ---
if __name__ == "__main__":
    print("🚀 Starting Flask server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🔧 Debug mode: ON")
    # The host '0.0.0.0' makes the server accessible from your network.
    app.run(debug=True, host='0.0.0.0', port=5000)
