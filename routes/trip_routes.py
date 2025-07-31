from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
# *** FIXED ***: Removed 'TravelTip' as it's not defined in the new models.py and wasn't being used in this file.
from models import db, User, Trip 
# from utils.itinerary_ai import ItineraryGenerator # This line was causing an error if the file doesn't exist.
# from routes.weather_routes import get_coordinates, get_weather as get_weather_data # This also causes circular import issues.

trip_bp = Blueprint("trips", __name__)
# ai_generator = ItineraryGenerator() # This should be initialized where it's used or passed in.

@trip_bp.route("/", methods=["GET"])
@jwt_required()
def get_user_trips():
    """
    Fetches a paginated and filterable list of trips for the logged-in user.
    """
    try:
        user_id = get_jwt_identity()
        
        # Basic query for the user's trips
        query = Trip.query.filter_by(user_id=user_id)

        # --- Filtering ---
        status = request.args.get("status")
        if status:
            query = query.filter_by(status=status)

        search = request.args.get("search")
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Trip.title.like(search_term)) |
                (Trip.destination_city.like(search_term)) |
                (Trip.destination_country.like(search_term))
            )
        
        # --- Sorting ---
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")
        if hasattr(Trip, sort_by):
            order_field = getattr(Trip, sort_by)
            query = query.order_by(order_field.desc() if sort_order == "desc" else order_field.asc())

        # --- Pagination ---
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 50) # Limit per_page to a max of 50
        
        trips_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        trips_data = [trip.to_dict(include_detailed=False) for trip in trips_paginated.items]

        return jsonify({
            "success": True,
            "data": {
                "trips": trips_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total_items": trips_paginated.total,
                    "total_pages": trips_paginated.pages,
                },
            },
        }), 200

    except Exception as e:
        # It's good practice to log the actual error for debugging
        print(f"Error fetching trips: {e}") 
        return jsonify({"success": False, "message": "An error occurred while fetching trips."}), 500


# NOTE: The '/generate-itinerary' route has been commented out as it depends on 
# 'itinerary_ai.py' and 'weather_routes.py', which were causing import errors.
# We can add this back once the main application is running smoothly.
#
# @trip_bp.route("/<int:trip_id>/generate-itinerary", methods=["POST"])
# @jwt_required()
# def generate_itinerary(trip_id):
#     # ... implementation ...
#     pass

