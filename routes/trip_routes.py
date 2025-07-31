# routes/trip_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Trip, TravelTip
from utils.itinerary_ai import ItineraryGenerator
from utils.external_api import get_coordinates, get_weather_data
from datetime import datetime, timedelta

trip_bp = Blueprint('trips', __name__)

# Initialize AI generator
ai_generator = ItineraryGenerator()

# -------------------------
# Get All Trips
# -------------------------
@trip_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_trips():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # Query params
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        status = request.args.get('status')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        query = Trip.query.filter_by(user_id=user_id)

        if status:
            query = query.filter_by(status=status)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Trip.title.like(search_term)) |
                (Trip.destination_city.like(search_term)) |
                (Trip.destination_country.like(search_term))
            )

        if hasattr(Trip, sort_by):
            order_field = getattr(Trip, sort_by)
            query = query.order_by(order_field.desc() if sort_order == 'desc' else order_field.asc())

        trips_paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        trips_data = [trip.to_dict(include_detailed=False) for trip in trips_paginated.items]

        return jsonify({
            'success': True,
            'data': {
                'trips': trips_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': trips_paginated.total,
                    'pages': trips_paginated.pages,
                    'has_next': trips_paginated.has_next,
                    'has_prev': trips_paginated.has_prev
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to fetch trips', 'error': str(e)}), 500


# -------------------------
# Get Single Trip
# -------------------------
@trip_bp.route('/<int:trip_id>', methods=['GET'])
@jwt_required()
def get_trip(trip_id):
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()

        if not trip:
            return jsonify({'success': False, 'message': 'Trip not found'}), 404

        return jsonify({'success': True, 'data': {'trip': trip.to_dict(include_detailed=True)}}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to fetch trip', 'error': str(e)}), 500


# -------------------------
# Create Trip
# -------------------------
@trip_bp.route('/', methods=['POST'])
@jwt_required()
def create_trip():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        required_fields = ['destination_city', 'destination_country', 'duration', 'budget_amount']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field} is required'}), 400

        # Validate duration
        duration = data['duration']
        if not isinstance(duration, int) or duration < 1 or duration > 30:
            return jsonify({'success': False, 'message': 'Duration must be between 1 and 30 days'}), 400

        # Validate budget
        budget_amount = data['budget_amount']
        if not isinstance(budget_amount, (int, float)) or budget_amount <= 0:
            return jsonify({'success': False, 'message': 'Budget must be a positive number'}), 400

        trip = Trip(
            user_id=user_id,
            title=data.get('title', '').strip(),
            destination_city=data['destination_city'].strip(),
            destination_country=data['destination_country'].strip(),
            duration=duration,
            budget_amount=budget_amount,
            budget_currency=data.get('budget_currency', 'USD'),
            travel_style=data.get('travel_style', user.travel_style),
            notes=data.get('notes', '').strip()
        )

        if not trip.title:
            trip.generate_title()

        # Interests
        interests = data.get('interests', user.get_interests())
        if interests:
            trip.set_interests(interests)

        # Coordinates
        if data.get('coordinates'):
            coords = data['coordinates']
            if coords.get('latitude') and coords.get('longitude'):
                trip.latitude = coords['latitude']
                trip.longitude = coords['longitude']
        else:
            lat, lng = get_coordinates(trip.destination_city, trip.destination_country)
            if lat and lng:
                trip.latitude, trip.longitude = lat, lng

        # Dates
        if data.get('start_date'):
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                trip.start_date = start_date
                trip.end_date = start_date + timedelta(days=duration - 1)
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid start_date format (use YYYY-MM-DD)'}), 400

        # Tags
        if data.get('tags'):
            trip.set_tags(data['tags'])

        db.session.add(trip)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Trip created', 'data': {'trip': trip.to_dict(include_detailed=True)}}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to create trip', 'error': str(e)}), 500


# -------------------------
# Generate Itinerary
# -------------------------
@trip_bp.route('/<int:trip_id>/generate-itinerary', methods=['POST'])
@jwt_required()
def generate_itinerary(trip_id):
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()

        if not trip:
            return jsonify({'success': False, 'message': 'Trip not found'}), 404

        user = User.query.get(user_id)

        destination_data = {
            'city': trip.destination_city,
            'country': trip.destination_country,
            'coordinates': {'latitude': trip.latitude, 'longitude': trip.longitude} if trip.latitude and trip.longitude else None
        }

        budget_data = {'amount': trip.budget_amount, 'currency': trip.budget_currency}
        preferences = {'travel_style': trip.travel_style or user.travel_style, 'preferred_activities': user.get_preferred_activities()}
        interests = trip.get_interests() or user.get_interests()

        itinerary_data = ai_generator.generate_itinerary(destination_data, trip.duration, interests, budget_data, preferences, trip.start_date)

        trip.set_itinerary_data(itinerary_data)
        trip.ai_generated = True
        trip.generation_model = 'gpt-3.5-turbo'

        if trip.latitude and trip.longitude and trip.start_date:
            weather_data = get_weather_data(trip.latitude, trip.longitude, trip.start_date, trip.duration)
            if weather_data:
                trip.set_weather_data(weather_data)

        db.session.commit()

        return jsonify({'success': True, 'message': 'Itinerary generated', 'data': {'trip': trip.to_dict(include_detailed=True)}}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to generate itinerary', 'error': str(e)}), 500


# -------------------------
# Update Trip
# -------------------------
@trip_bp.route('/<int:trip_id>', methods=['PUT'])
@jwt_required()
def update_trip(trip_id):
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()

        if not trip:
            return jsonify({'success': False, 'message': 'Trip not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        updatable_fields = ['title', 'destination_city', 'destination_country', 'duration', 'budget_amount', 'budget_currency', 'travel_style', 'notes', 'status']
        for field in updatable_fields:
            if field in data:
                setattr(trip, field, data[field])

        if 'interests' in data:
            trip.set_interests(data['interests'])

        if 'coordinates' in data:
            coords = data['coordinates']
            if coords.get('latitude') and coords.get('longitude'):
                trip.latitude, trip.longitude = coords['latitude'], coords['longitude']

        if 'start_date' in data:
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                trip.start_date = start_date
                trip.end_date = start_date + timedelta(days=trip.duration - 1)
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid start_date format'}), 400

        if 'tags' in data:
            trip.set_tags(data['tags'])

        if 'itinerary_data' in data:
            trip.set_itinerary_data(data['itinerary_data'])

        if 'is_favorite' in data:
            trip.is_favorite = bool(data['is_favorite'])

        db.session.commit()

        return jsonify({'success': True, 'message': 'Trip updated', 'data': {'trip': trip.to_dict(include_detailed=True)}}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to update trip', 'error': str(e)}), 500


# -------------------------
# Delete Trip
# -------------------------
@trip_bp.route('/<int:trip_id>', methods=['DELETE'])
@jwt_required()
def delete_trip(trip_id):
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()

        if not trip:
            return jsonify({'success': False, 'message': 'Trip not found'}), 404

        db.session.delete(trip)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Trip deleted'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to delete trip', 'error': str(e)}), 500


# -------------------------
# Duplicate Trip
# -------------------------
@trip_bp.route('/<int:trip_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_trip(trip_id):
    try:
        user_id = get_jwt_identity()
        original_trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()

        if not original_trip:
            return jsonify({'success': False, 'message': 'Trip not found'}), 404

        new_trip = Trip(
            user_id=user_id,
            title=f"{original_trip.title} (Copy)",
            destination_city=original_trip.destination_city,
            destination_country=original_trip.destination_country,
            duration=original_trip.duration,
            budget_amount=original_trip.budget_amount,
            budget_currency=original_trip.budget_currency,
            travel_style=original_trip.travel_style,
            notes=original_trip.notes,
            latitude=original_trip.latitude,
            longitude=original_trip.longitude,
            start_date=original_trip.start_date,
            end_date=original_trip.end_date,
            is_favorite=original_trip.is_favorite
        )

        new_trip.set_interests(original_trip.get_interests())
        new_trip.set_tags(original_trip.get_tags())
        new_trip.set_itinerary_data(original_trip.get_itinerary_data())
        new_trip.set_weather_data(original_trip.get_weather_data())

        db.session.add(new_trip)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Trip duplicated', 'data': {'trip': new_trip.to_dict(include_detailed=True)}}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to duplicate trip', 'error': str(e)}), 500
