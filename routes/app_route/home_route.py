from datetime import datetime, timedelta
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models.user_location_model import User_Location
from models.user_model import User
from config.db_config import (
    PLACE_COLLECTION,
    ACTIVITY_COLLECTION,
    USER_COLLECTION,
    CITY_COLLECTION,
)
from utils.helper import apply_filters, find_closest_place, format_event, protected


home_bp = Blueprint("home", __name__)


@home_bp.route("/OperationRequest", methods=["POST"])
@protected
def operation_route():
    data = request.get_json()
    if data["StoredProcedureName"] == "APP_UserLocation_Insert":
        try:
            data = request.get_json()

            place_id = find_closest_place(
                PLACE_COLLECTION,
                float(data.get("Params1")),
                float(data.get("Params2")),
                40,
            )

            _id = str(uuid.uuid4())

            user_data = {
                "PlaceId": place_id,
                "CityId": data.get("Params3", ""),
                "Longitude": data.get("Params2", ""),
                "Latitude": data.get("Params1", ""),
                "UserLocationId": data.get("userId", ""),
                "_id": _id,
                "CreatedBy": get_jwt_identity(),
            }

            inserted_id = User_Location.insert_user_location(user_data)
            return (
                jsonify(
                    {"message": "user location added successfully", "id": inserted_id}
                ),
                201,
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif data["StoredProcedureName"] == "EventViewModifications":

        data = request.get_json()
        user_id = data.get("Params3")
        event_id = data.get("Params1")
        action = data.get("Params2")  # "add" or "remove"

        if not user_id or not event_id or action not in ["INSERT", "DELETE"]:
            return (
                jsonify(
                    {
                        "message": "userId, eventId, and a valid action ('add' or 'remove') are required"
                    }
                ),
                400,
            )

        update_query = (
            {"$addToSet": {"favourite.favouriteEvent": event_id}}
            if action == "INSERT"
            else {"$pull": {"favourite.favouriteEvent": event_id}}
        )

        # Update the user document
        USER_COLLECTION.update_one({"_id": user_id}, update_query)

        message = (
            "Event added to favourites"
            if action == "INSERT"
            else "Event removed from favourites"
        )
        return jsonify({"message": message}), 200

    elif data["StoredProcedureName"] == "PlaceViewModifications":

        data = request.get_json()
        user_id = data.get("Params3")
        event_id = data.get("Params1")
        action = data.get("Params2")  # "add" or "remove"

        if not user_id or not event_id or action not in ["INSERT", "DELETE"]:
            return (
                jsonify(
                    {
                        "message": "userId, placeId, and a valid action ('add' or 'remove') are required"
                    }
                ),
                400,
            )

        update_query = (
            {"$addToSet": {"favourite.favouritePlace": event_id}}
            if action == "INSERT"
            else {"$pull": {"favourite.favouritePlace": event_id}}
        )

        # Update the user document
        USER_COLLECTION.update_one({"_id": user_id}, update_query)

        message = (
            "Place added to favourites"
            if action == "INSERT"
            else "Place removed from favourites"
        )
        return jsonify({"message": message}), 200


@home_bp.route("/RequestForJson", methods=["POST"])
@protected
def request_json_route():
    data = request.get_json()

    if data["StoredProcedureName"] == "GetEvents":
        now = datetime.utcnow()
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        start_of_week = start_of_today - timedelta(
            days=start_of_today.weekday()
        )  # Monday start
        end_of_week = start_of_week + timedelta(
            days=6, hours=23, minutes=59, seconds=59
        )

        # Fetch all events
        user_id = data.get("userId", "")
        city_id = data.get("Params1", "")

        user = USER_COLLECTION.find_one(
            {"_id": user_id}, {"favourite.favouriteEvent": 1}
        )
        print("user : ", user)
        events = list(
            ACTIVITY_COLLECTION.find(
                {
                    "CityId": city_id,
                    "ActivityType": {"$regex": "^EVENT$", "$options": "i"},
                }
            )
        )

        tonight_events = []
        this_week_events = []
        upcoming_events = []

        for event in events:
            # if isinstance(activity_date, str):
            #     try:
            #         activity_date = datetime.strptime(activity_date, "%Y-%m-%dT%H:%M:%S")  # Adjust format if needed
            #     except ValueError:
            #         activity_date = None  # Skip invalid dates
            migrated_date = event.get("MigratedDate")

            if isinstance(migrated_date, str):
                try:
                    print("migrated d ate ")
                    migrated_date = datetime.strptime(
                        migrated_date, "%Y-%m-%dT%H:%M:%S"
                    )  # Adjust format if needed
                except ValueError:
                    migrated_date = None  # Skip invalid dates

            # Categorize events
            formatted_event = format_event(event, user["favourite"]["favouriteEvent"])

            if migrated_date and start_of_today <= migrated_date <= end_of_today:
                tonight_events.append(formatted_event)
            elif migrated_date and start_of_week <= migrated_date <= end_of_week:
                this_week_events.append(formatted_event)
            else:
                upcoming_events.append(formatted_event)

            # Response formatting
        response = {
            "success": True,
            "data": {
                "tonight": tonight_events,
                "thisWeek": this_week_events,
                "upcoming": upcoming_events,
            },
        }

        return jsonify(response), 200

    elif data["StoredProcedureName"] == "APP_City_Search":
        city_name = data.get("Params1", "")

        cities = list(
            CITY_COLLECTION.find({"CityName": {"$regex": city_name, "$options": "i"}})
        )

        return jsonify({"success": True, "data": cities}), 200

    elif data["StoredProcedureName"] == "APP_UserFavouritesScreen":
        user_id = data.get("Params1", "")
        user = USER_COLLECTION.find_one({"_id": user_id}, {"favourite": 1})
        if not user or "favourite" not in user:
            return jsonify({"message": "User not found or no favorites"}), 404

        # Extract favorite event and place IDs
        favourite_event_ids = user["favourite"].get("favouriteEvent", [])
        favourite_place_ids = user["favourite"].get("favouritePlace", [])

        # Fetch full event details
        favourite_events = list(
            ACTIVITY_COLLECTION.find({"ActivityId": {"$in": favourite_event_ids}})
        )

        # Fetch full place details
        favourite_places = list(
            PLACE_COLLECTION.find({"PlaceId": {"$in": favourite_place_ids}})
        )

        response = {
            "success":True,
            "data": {
                "favouriteEvents": favourite_events,
                "favouritePlaces": favourite_places,
            }
        }

        return jsonify(response), 200
