from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Trip, TravelTip
from utils.itinerary_ai import ItineraryGenerator
from routes.weather_routes import get_coordinates, get_weather as get_weather_data
from datetime import datetime, timedelta

trip_bp = Blueprint("trips", __name__)
ai_generator = ItineraryGenerator()


@trip_bp.route("/", methods=["GET"])
@jwt_required()
def get_user_trips():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 50)
        status = request.args.get("status")
        search = request.args.get("search")
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")

        query = Trip.query.filter_by(user_id=user_id)

        if status:
            query = query.filter_by(status=status)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Trip.title.like(search_term))
                | (Trip.destination_city.like(search_term))
                | (Trip.destination_country.like(search_term))
            )
        if hasattr(Trip, sort_by):
            order_field = getattr(Trip, sort_by)
            query = query.order_by(order_field.desc() if sort_order == "desc" else order_field.asc())

        trips_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        trips_data = [trip.to_dict(include_detailed=False) for trip in trips_paginated.items]

        return jsonify(
            {
                "success": True,
                "data": {
                    "trips": trips_data,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": trips_paginated.total,
                        "pages": trips_paginated.pages,
                        "has_next": trips_paginated.has_next,
                        "has_prev": trips_paginated.has_prev,
                    },
                },
            }
        ), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to fetch trips", "error": str(e)}), 500


@trip_bp.route("/<int:trip_id>/generate-itinerary", methods=["POST"])
@jwt_required()
def generate_itinerary(trip_id):
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not trip:
            return jsonify({"success": False, "message": "Trip not found"}), 404

        user = User.query.get(user_id)
        destination_data = {
            "city": trip.destination_city,
            "country": trip.destination_country,
            "coordinates": {"latitude": trip.latitude, "longitude": trip.longitude}
            if trip.latitude and trip.longitude else None,
        }

        budget_data = {"amount": trip.budget_amount, "currency": trip.budget_currency}
        preferences = {
            "travel_style": trip.travel_style or user.travel_style,
            "preferred_activities": user.get_preferred_activities(),
        }
        interests = trip.get_interests() or user.get_interests()

        itinerary_data = ai_generator.generate_itinerary(
            destination_data, trip.duration, interests, budget_data, preferences, trip.start_date
        )

        trip.set_itinerary_data(itinerary_data)
        trip.ai_generated = True
        trip.generation_model = "gemini-1.5-flash"

        if trip.latitude and trip.longitude and trip.start_date:
            weather_data = get_weather_data(trip.latitude, trip.longitude, trip.start_date, trip.duration)
            if weather_data:
                trip.set_weather_data(weather_data)

        db.session.commit()
        return jsonify({"success": True, "message": "Itinerary generated", "data": {"trip": trip.to_dict(include_detailed=True)}}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Failed to generate itinerary", "error": str(e)}), 500
