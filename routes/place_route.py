import uuid
from flask import Blueprint, request, jsonify
from models.place_model import Place
from utils.helper import apply_filters


place_bp = Blueprint("place", __name__)

# ✅ Get Places (Read with Filters & Pagination)
@place_bp.route("/", methods=["POST"])
def get_places():
    """Fetch places using filters and pagination."""
    try:
        data = request.get_json()
        filters = apply_filters({}, data.get("filterInfo", []))
        page = int(data.get("page", 1))
        page_size = int(data.get("pageSize", 10))

        result = Place.get_places(filters, page, page_size)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Create a New Place
@place_bp.route("/insert", methods=["POST"])
def create_place():
    """Insert a new place into the database."""
    try:
        place_data = request.get_json()
        _id=str(uuid.uuid4())
        place_data["PlaceId"]=_id
        place_data["_id"]=_id
        inserted_id = Place.insert_place(place_data)
        return jsonify({"message": "Place added successfully", "id": inserted_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Update an Existing Place
@place_bp.route("/update", methods=["POST"])
def update_place():
    """Update an existing place by PlaceId."""
    try:
        data = request.get_json()
        place_id=data.get("PlaceId")
        data.pop("PlaceId")
        print(place_id)
        print(data)
        updated = Place.update_place(place_id, data)
        if updated:
            return jsonify({"message": "Place updated successfully"}), 200
        else:
            return jsonify({"error": "Place not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ✅ Update current popularity Multiple
@place_bp.route("/update", methods=["POST"])
def update_place():
    """Update an existing place by PlaceId."""
    try:
        data = request.get_json()
        print(data)
        updated = Place.update_many(data)
        if updated:
            return jsonify({"message": "Place updated successfully"}), 200
        else:
            return jsonify({"error": "Place not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Delete a Place
@place_bp.route("/delete", methods=["POST"])
def delete_place(place_id):
    """Delete a place by PlaceId."""
    try:
        data = request.get_json()
        place_id=data.get("PlaceId")
        deleted = Place.delete_place(place_id)
        if deleted:
            return jsonify({"message": "Place deleted successfully"}), 200
        else:
            return jsonify({"error": "Place not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
