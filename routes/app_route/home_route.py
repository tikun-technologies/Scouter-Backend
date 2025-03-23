from datetime import datetime, timedelta
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models.user_location_model import User_Location
from models.notification_model import Notification
from config.db_config import (
    PLACE_COLLECTION,
    ACTIVITY_COLLECTION,
    USER_COLLECTION,
    USER_DEVICE_COLLECTION,
    USER_LOCATION_COLLECTION,
    CITY_COLLECTION,
    NOTIFICATION_COLLECTION,
)
from utils.helper import apply_filters, find_closest_place, format_event, get_activities, haversine_distance, protected, send_notifications_to_all, upload_to_azure


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
            response = {"success": True, "data": [{"result": "SUCCESS_INSERT"}]}

            return (
                jsonify(response),
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
        response = {"success": True, "data": [{"result": message}]}
        return jsonify(response), 200

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
        response = {"success": True, "data": [{"result": message}]}
        return jsonify(response), 200

    elif data["StoredProcedureName"] == "UpdateCommentsLike":
        activity_id = data.get("Params1")
        per2 = data.get("Params2")

        if not activity_id:
            return jsonify({"error": "ActivityId is required"}), 400

        # Find the activity
        activity = ACTIVITY_COLLECTION.find_one({"ActivityId": activity_id})

        if not activity:
            return jsonify({"error": "Activity not found"}), 404

        # Increase LikeCount by 1 (default to 0 if it doesn't exist)
        if per2 == "Like":
            new_like_count = (activity.get("LikeCount") or 0) + 1
            message = "like increased by 1"
        else:
            new_like_count = max((activity.get("LikeCount") or 1) - 1, 0)
            message = "like decreased by 1"

        # Update in the database
        ACTIVITY_COLLECTION.update_one(
            {"ActivityId": activity_id}, {"$set": {"LikeCount": new_like_count}}
        )

        response = {"success": True, "data": [{"result": message}]}
        return jsonify(response), 200


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
            "success": True,
            "data": {
                "favouriteEvents": favourite_events,
                "favouritePlaces": favourite_places,
            },
        }

        return jsonify(response), 200


@home_bp.route("/UserLocation_Insert", methods=["POST"])
@protected
def UserLocation_Insert():
    data = request.get_json()
    try:
        data = request.get_json()

        place_id = find_closest_place(
            PLACE_COLLECTION,
            float(data.get("latitude")),
            float(data.get("longitude")),
            40,
        )

        _id = str(uuid.uuid4())

        user_data = {
            "PlaceId": place_id,
            "CityId": data.get("cityId", ""),
            "Longitude": data.get("longitude", ""),
            "Latitude": data.get("latitude", ""),
            "UserLocationId": data.get("userId", ""),
            "_id": _id,
            "CreatedBy": get_jwt_identity(),

        }

        inserted_id = User_Location.insert_user_location(user_data)
        response = {"success": True, "data": [{"result": "SUCCESS_INSERT"}]}

        return (
            jsonify(response),
            201,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@home_bp.route("/GetEvents", methods=["POST"])
@protected
def GetEvents():
    data = request.get_json()

    now = datetime.utcnow()
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    start_of_week = start_of_today - timedelta(
        days=start_of_today.weekday()
    )  # Monday start
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

    # Fetch all events
    user_id = data.get("userId", "")
    city_id = data.get("cityId", "")

    user = USER_COLLECTION.find_one({"_id": user_id}, {"favourite.favouriteEvent": 1})
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


@home_bp.route("/update-activity", methods=["POST"])
@protected
def update_activity():
    data = data = request.get_json()
    try:

        user_id = data.get("userId")
        activity_id = data.get("activityId")
        action = data.get("action")

        if not user_id or not action:
            return jsonify({"error": "UserId and Action are required"}), 400

        update_query = {}

        if action == "like":
            update_query = {
                "$addToSet": {"LikedUsers": user_id},
                "$inc": {"LikeCount": 1},
            }
        elif action == "dislike":
            update_query = {"$pull": {"LikedUsers": user_id}, "$inc": {"LikeCount": -1}}
        elif action == "flag":
            update_query = {
                "$addToSet": {"FlaggedUsers": user_id},
                "$set": {"IsFlagged": True},
            }
        elif action == "unflag":
            update_query = {
                "$pull": {"FlaggedUsers": user_id},
                "$set": {"IsFlagged": False},
            }
        elif action == "view":
            update_query = {
                "$addToSet": {"ViewedUsers": user_id},
                "$inc": {"ViewCount": 1},
            }
        else:
            return jsonify({"error": "Invalid action"}), 400

        result = ACTIVITY_COLLECTION.update_one({"_id": activity_id}, update_query)

        if result.matched_count == 0:
            message = "Activity not found"
        else:
            message = f"Activity {action} successfully"
        response = {"success": True, "message": message}

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@home_bp.route("/user-favourite-screen", methods=["POST"])
@protected
def user_favourite_screen():
    data = request.get_json()
    user_id = data.get("userId", "")
    user = USER_COLLECTION.find_one({"_id": user_id}, {"favourite": 1})
    if not user:
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
        "success": True,
        "data": {
            "favouriteEvents": favourite_events,
            "favouritePlaces": favourite_places,
        },
    }

    return jsonify(response), 200


@home_bp.route("/user-favourite", methods=["POST"])
@protected
def user_favourite():
    data = request.get_json()
    user_id = data.get("userId")
    action = data.get("action")
    if not user_id or not action:
        return (
            jsonify(
                {
                    "message": "userId, placeId, and a valid action ('add' or 'remove') are required"
                }
            ),
            400,
        )

    if data.get("eventId"):
        event_id = data.get("eventId")
        action = data.get("action")
        update_query = (
            {"$addToSet": {"favourite.favouriteEvent": event_id}}
            if action == "EVENT-INSERT"
            else {"$pull": {"favourite.favouriteEvent": event_id}}
        )

        # Update the user document
        USER_COLLECTION.update_one({"_id": user_id}, update_query)

        message = (
            "Event added to favourites"
            if action == "EVENT-INSERT"
            else "Event removed from favourites"
        )
        response = {"success": True, "data": [{"result": message}]}
        return jsonify(response), 200
    else:
        place_id = data.get("placeId")
        action = data.get("action")
        update_query = (
            {"$addToSet": {"favourite.favouritePlace": place_id}}
            if action == "PLACE-INSERT"
            else {"$pull": {"favourite.favouritePlace": place_id}}
        )

        # Update the user document
        USER_COLLECTION.update_one({"_id": user_id}, update_query)

        message = (
            "Place added to favourites"
            if action == "PLACE-INSERT"
            else "Place removed from favourites"
        )
        response = {"success": True, "data": [{"result": message}]}
        return jsonify(response), 200


@home_bp.route("/city-search", methods=["POST"])
@protected
def city_search():
    data = request.get_json()
    city_name = data.get("name", "")

    cities = list(
        CITY_COLLECTION.find({"CityName": {"$regex": city_name, "$options": "i"}})
    )

    return jsonify({"success": True, "data": cities}), 200


@home_bp.route("/place-search", methods=["POST"])
@protected
def place_search():
    data = request.get_json()
    place_name = data.get("name", "")

    places = list(
        PLACE_COLLECTION.find({"PlaceName": {"$regex": place_name, "$options": "i"}})
    )

    return jsonify({"success": True, "data": places}), 200


@home_bp.route("/map-places", methods=["POST"])
@protected
def get_map_places():
    data = request.get_json()
    city_id = data.get("cityId")
    places =list( PLACE_COLLECTION.find(
        {"CityId": city_id},
        {
            "_id":1,
            "PlaceName": 1,
            "Latitude": 1,
            "Longitude": 1,
            "CurrentPopularity": 1,
            "Address": 1,
        },
    ))
    return jsonify({"success": True, "data": places}), 200



@home_bp.route("/map-place-info", methods=["POST"])
@protected
def get_map_place_info():
    data = request.get_json()
    place_Id = data.get("placeId")
    latitude=data.get("latitude")
    longitude=data.get("longitude")
    get=data.get("get")
    page = int(data.get("page", 1))
    page_size = int(data.get("pageSize", 10))
    place=PLACE_COLLECTION.find_one({"PlaceId":place_Id})
    place["Distance_km"], place["Distance_mil"] = haversine_distance(
    latitude, longitude, place["Latitude"], place["Longitude"]
)
    if get=="posts":
        posts = get_activities(place_Id,page,page_size)
        # posts["data"] = list(map(transform_activity, posts["data"]))
        posts["place"]=place
            
        return jsonify(posts), 200
    elif get=="events":
        
        data = request.get_json()

        now = datetime.utcnow()
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        start_of_week = start_of_today - timedelta(
            days=start_of_today.weekday()
        )  # Monday start
        end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

        # Fetch all events
        user_id = data.get("userId", "")
        user = USER_COLLECTION.find_one({"_id": user_id}, {"favourite.favouriteEvent": 1})
        print("user : ", user)
        events = list(
            ACTIVITY_COLLECTION.find(
                {
                    "PlaceId": place_Id,
                    "ActivityType": {"$regex": "^EVENT$", "$options": "i"},
                }
            )
        )

        tonight_events = []
        this_week_events = []
        upcoming_events = []

        for event in events:

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
            "place":place,
            "data": {
                "events":{
                "tonight": tonight_events,
                "thisWeek": this_week_events,
                "upcoming": upcoming_events,
            }},
        }
        return jsonify( response), 200
 
