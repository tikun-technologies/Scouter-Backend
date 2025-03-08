import uuid
from flask import Blueprint, request, jsonify
from models.activity_model import Activity
from utils.helper import apply_filters


activity_bp = Blueprint("activity", __name__)

# ✅ Get activitys (Read with Filters & Pagination)
@activity_bp.route("/", methods=["POST"])
def get_activitys():
    """Fetch activitys using filters and pagination."""
    try:
        data = request.get_json()
        filters = apply_filters({}, data.get("filterInfo", []))
        page = int(data.get("page", 1))
        page_size = int(data.get("pageSize", 10))

        result = Activity.get_activity(filters, page, page_size)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Create a New activity
@activity_bp.route("/insert", methods=["POST"])
def create_activity():
    """Insert a new activity into the database."""
    try:
        activity_data = request.get_json()
        _id=str(uuid.uuid4())
        activity_data["activityId"]=_id
        activity_data["_id"]=_id
        inserted_id = Activity.insert_place(activity_data)
        return jsonify({"message": "activity added successfully", "id": inserted_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Update an Existing activity
@activity_bp.route("/update", methods=["POST"])
def update_activity():
    """Update an existing activity by activityId."""
    try:
        data = request.get_json()
        activity_id=data.get("activityId")
        data.pop("activityId")
        print(activity_id)
        print(data)
        updated = Activity.update_activity(activity_id, data)
        if updated:
            return jsonify({"message": "activity updated successfully"}), 200
        else:
            return jsonify({"error": "activity not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Delete a activity
@activity_bp.route("/delete", methods=["POST"])
def delete_activity(activity_id):
    """Delete a activity by activityId."""
    try:
        data = request.get_json()
        activity_id=data.get("ActivityId")
        deleted = Activity.delete_activity(activity_id)
        if deleted:
            return jsonify({"message": "activity deleted successfully"}), 200
        else:
            return jsonify({"error": "activity not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
