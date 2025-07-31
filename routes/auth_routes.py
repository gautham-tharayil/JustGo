from flask import Blueprint, request, jsonify
from models import db, User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data.get("email") or not data.get("password"):
        return jsonify({"success": False, "message": "Email and password required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"success": False, "message": "User already exists"}), 400

    new_user = User(
        username=data.get("username"),
        email=data["email"]
    )
    new_user.set_password(data["password"])  # ✅ hashes the password
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"success": True, "message": "User registered successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()

    if not user or not user.check_password(data.get("password")):
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    user.update_last_login()  # ✅ update last_login field
    access_token = create_access_token(identity=user.id)
    return jsonify({"success": True, "token": access_token, "user": user.to_dict()}), 200
