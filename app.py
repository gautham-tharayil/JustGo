import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Import your database and blueprint objects
from models import db
from routes.auth_routes import auth_bp
from routes.trip_routes import trip_bp
from routes.weather_routes import weather_bp

# Load environment variables from a .env file
load_dotenv()

def create_app():
    """
    Application factory function to create and configure the Flask app.
    """
    app = Flask(__name__)

    # --- Configuration ---
    # Load configuration from environment variables or a config object
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your-fallback-secret-key")
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "your-fallback-jwt-secret")
    
    # Database configuration
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "travel_planner.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- Initialize Extensions ---
    db.init_app(app)
    JWTManager(app)
    # Apply CORS to all routes starting with /api/
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})

    # --- Register Blueprints ---
    # This is the crucial step that connects your route files to the app.
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(trip_bp, url_prefix='/api/trips')
    app.register_blueprint(weather_bp, url_prefix='/api/weather')

    # --- Create Database Tables ---
    # The app context is needed for SQLAlchemy to know which app instance to work with.
    with app.app_context():
        db.create_all()
        print(f"✅ Database tables created at: {db_path}")

    return app

# --- App Runner ---
if __name__ == "__main__":
    app = create_app()
    print("🚀 Starting Flask server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🔧 Debug mode: ON")
    app.run(debug=True, host='0.0.0.0', port=5000)
