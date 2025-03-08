import uuid
from flask import Blueprint, request, jsonify
from models.user_model import User
from utils.helper import apply_filters


user_bp = Blueprint("user", __name__)

# ✅ Get users (Read with Filters & Pagination)
@user_bp.route("/", methods=["POST"])
def get_users():
    """Fetch users using filters and pagination."""
    try:
        data = request.get_json()
        filters = apply_filters({}, data.get("filterInfo", []))
        page = int(data.get("page", 1))
        page_size = int(data.get("pageSize", 10))

        result = User.get_users(filters, page, page_size)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Create a New user
@user_bp.route("/insert", methods=["POST"])
def create_user():
    """Insert a new user into the database."""
    try:
        user_data = request.get_json()
        _id=str(uuid.uuid4())
        user_data["UserId"]=_id
        user_data["_id"]=_id
        inserted_id = User.insert_user(user_data)
        return jsonify({"message": "user added successfully", "id": inserted_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Update an Existing user
@user_bp.route("/update", methods=["POST"])
def update_user():
    """Update an existing user by UserId."""
    try:
        data = request.get_json()
        user_id=data.get("UserId")
        data.pop("UserId")
        print(user_id)
        print(data)
        updated = User.update_user(user_id, data)
        if updated:
            return jsonify({"message": "user updated successfully"}), 200
        else:
            return jsonify({"error": "user not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# ✅ Delete a user
@user_bp.route("/delete", methods=["POST"])
def delete_user(user_id):
    """Delete a user by UserId."""
    try:
        data = request.get_json()
        user_id=data.get("UserId")
        deleted = User.delete_user(user_id)
        if deleted:
            return jsonify({"message": "user deleted successfully"}), 200
        else:
            return jsonify({"error": "user not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
