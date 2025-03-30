import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models.place_model import Place
from utils.helper import apply_filters, haversine_distance, protected, upload_multiple_files


place_bp = Blueprint("place", __name__)


# ✅ Get Places (Read with Filters & Pagination)
@place_bp.route("/list", methods=["POST"])
@protected
def get_places():
    """Fetch places using filters and pagination."""
    try:
        data = request.get_json()
        print(data)
        filters = apply_filters({}, data)
        page = int(data.get("page", 1))
        page_size = int(data.get("pageSize", 10))
        include_distance = data.get("IncludeCalculateDistance", False)
        user_lat = data.get("Latitude")
        user_lon = data.get("Longitude")
        user_id = data.get("userId", None)
        WithInDistance = data.get("WithInDistance", None)
        if user_id==None:
            return jsonify({"error": "User Id should not be null"}), 500
        result = Place.get_places(filters,user_id, user_lat,user_lon,WithInDistance, page, page_size)
       
        if include_distance:
           
            
            if user_lat is None or user_lon is None:
                return jsonify({"error": "Latitude and Longitude are required for distance calculation"}), 400

            # Calculate distance for each place
            for place in result["data"]:
                place_lat = place.get("Latitude")
                place_lon = place.get("Longitude")

                if place_lat is not None and place_lon is not None:
                    place["Distance_km"], place["Distance_mil"] = haversine_distance(user_lat, user_lon, place_lat, place_lon)  # Distance in meters
        
        return jsonify(result), 200
       
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Create a New Place
@place_bp.route("/insert", methods=["POST"])
@protected
def create_place():
    """Insert a new place into the database."""
    try:
        place_data = request.get_json()
        _id = str(uuid.uuid4())
        place_data["PlaceId"] = _id
        place_data["_id"] = _id
        place_data["CreatedBy"] = get_jwt_identity()
        place_data["location"] = {
            "type": "Point",
            "coordinates": [float(place_data["Longitude"]), float(place_data["Latitude"])],
        }
        try:
            place_data["ImagesUrl"] = ",".join(
                upload_multiple_files(place_data["MigratedImages"].split(","))
            )
            place_data.pop("MigratedImages")
        except:
            pass
        
        inserted_id = Place.insert_place(place_data)
        return jsonify({"message": "Place added successfully", "id": inserted_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Update an Existing Place
@place_bp.route("/update", methods=["POST"])
@protected
def update_place():
    """Update an existing place by PlaceId."""
    try:
        data = request.get_json()
        place_id = data.get("PlaceId")
        data.pop("PlaceId")
        print(place_id)
        print(data)
        try:
            data["ImagesUrl"] = ",".join(
                upload_multiple_files(data["MigratedImages"].split(","))
            )
            data.pop("MigratedImages")
        except:
            pass
        updated = Place.update_place(place_id, data)
        if updated:
            return jsonify({"message": "Place updated successfully"}), 200
        else:
            return jsonify({"error": "Place not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Update current popularity Multiple
@place_bp.route("/update-many", methods=["POST"])
@protected
def update_current_popularity():
    """Update an existing place by PlaceId."""
    try:
        data = request.get_json()
        # print(data)
        updated = Place.update_many(data)
        if updated:
            return jsonify({"message": "Place updated successfully"}), 200
        else:
            return jsonify({"error": "Place not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Delete a Place
@place_bp.route("/delete", methods=["POST"])
@protected
def delete_place(place_id):
    """Delete a place by PlaceId."""
    try:
        data = request.get_json()
        place_id = data.get("PlaceId")
        deleted = Place.delete_place(place_id)
        if deleted:
            return jsonify({"message": "Place deleted successfully"}), 200
        else:
            return jsonify({"error": "Place not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
