import uuid
from flask import Blueprint, request, jsonify
from models.user_location_model import User_Location
from utils.helper import apply_filters,protected


user_location_bp = Blueprint("user_location", __name__)

# ✅ Get users (Read with Filters & Pagination)
@user_location_bp.route("/list", methods=["POST"])
@protected
def get_user_locations():
    """Fetch users using filters and pagination."""
    try:
        data = request.get_json()
        filters = apply_filters({}, data.get("filterInfo", []))
        page = int(data.get("page", 1))
        page_size = int(data.get("pageSize", 10))

        result = User_Location.get_user_locations(filters, page, page_size)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Create a New user
@user_location_bp.route("/insert", methods=["POST"])
@protected
def create_user_location():
    """Insert a new user into the database."""
    try:
        user_data = request.get_json()
        _id=str(uuid.uuid4())
        user_data["UserLocationId"]=_id
        user_data["_id"]=_id
        inserted_id = User_Location.insert_user_location(user_data)
        return jsonify({"message": "user added successfully", "id": inserted_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Update an Existing user
@user_location_bp.route("/update", methods=["POST"])
@protected
def update_user_location():
    """Update an existing user by UserId."""
    try:
        data = request.get_json()
        user_id=data.get("UserLocationId")
        data.pop("UserLocationId")
        print(user_id)
        print(data)
        updated = User_Location.update_or_insert_user_location(user_id, data)
        if updated:
            return jsonify({"message": "user updated successfully"}), 200
        else:
            return jsonify({"error": "user not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# ✅ Delete a user
@user_location_bp.route("/delete", methods=["POST"])
@protected
def delete_user_location(user_id):
    """Delete a user by UserId."""
    try:
        data = request.get_json()
        user_id=data.get("UserLocationId")
        deleted = User_Location.delete_user_device(user_id)
        if deleted:
            return jsonify({"message": "user deleted successfully"}), 200
        else:
            return jsonify({"error": "user not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
