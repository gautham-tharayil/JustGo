import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --- Application Setup ---
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "a-default-secret-key")
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})

# --- In-Memory Data Store (No Database) ---
# We use simple lists of dictionaries to store data.
users = []
trips = {
    # We'll store trips by user email for easy access
}

# Helper function to find a user
def find_user_by_email(email):
    return next((user for user in users if user['email'] == email), None)

# --- API Routes ---

# --- Auth Routes ---
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    if find_user_by_email(email):
        return jsonify({"success": False, "message": "User already exists"}), 400
    
    # In a real app, you MUST hash passwords. For simplicity, we are storing it directly.
    new_user = {"id": len(users) + 1, "email": email, "password": password}
    users.append(new_user)
    
    # Initialize an empty list of trips for the new user
    trips[email] = []

    return jsonify({"success": True, "message": "User registered successfully"}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    user = find_user_by_email(email)

    # IMPORTANT: Comparing passwords in plain text is not secure.
    # This is done only to simplify the example by removing the database and hashing.
    if not user or user['password'] != password:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user['email'])
    return jsonify({
        "success": True, 
        "token": access_token, 
        "user": {"id": user['id'], "email": user['email']}
    }), 200

# --- Trip & Dashboard Routes ---
@app.route("/api/trips/dashboard-overview", methods=["GET"])
@jwt_required()
def get_dashboard_overview():
    current_user_email = get_jwt_identity()
    user_trips = trips.get(current_user_email, [])
    
    overview_data = {
        "welcome": "Welcome to your In-Memory Travel Planner!",
        "user_stats": {
            "total_trips": len(user_trips), 
            "upcoming_trips": len(user_trips), # Simplified for this example
            "completed_trips": 0 # Simplified for this example
        }
    }
    return jsonify(overview_data)

@app.route("/api/trips/", methods=["GET"])
@jwt_required()
def get_user_trips():
    current_user_email = get_jwt_identity()
    
    # If this is the first time a user logs in, create some mock data for them.
    if not trips.get(current_user_email):
        trips[current_user_email] = [
            {"id": 1, "title": "Summer in Paris", "destination_city": "Paris", "destination_country": "France"},
            {"id": 2, "title": "Tokyo Adventure", "destination_city": "Tokyo", "destination_country": "Japan"},
        ]
        
    user_trips = trips.get(current_user_email, [])
    
    return jsonify({"success": True, "data": {"trips": user_trips}}), 200

# --- App Runner ---
if __name__ == "__main__":
    print("🚀 Starting Flask server (No Database)...")
    app.run(debug=True, host='0.0.0.0', port=5000)
