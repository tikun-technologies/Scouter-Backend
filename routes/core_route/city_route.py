import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models.city_model import City
from utils.helper import apply_filters,protected


city_bp = Blueprint("city", __name__)

# ✅ Get citys (Read with Filters & Pagination)
@city_bp.route("/list", methods=["POST"])
@protected
def get_citys():
    """Fetch citys using filters and pagination."""
    try:
        data = request.get_json()
        filters = apply_filters({}, data)
        page = int(data.get("page", 1))
        page_size = int(data.get("pageSize", 10))
        result = City.get_citys(filters, page, page_size)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Create a New city
@city_bp.route("/insert", methods=["POST"])
@protected
def create_city():
    """Insert a new city into the database."""
    try:
        city_data = request.get_json()
        _id=str(uuid.uuid4())
        city_data["CityId"]=_id
        city_data["_id"]=_id
        city_data["CreatedBy"]=get_jwt_identity()
        inserted_id = City.insert_city(city_data)
        return jsonify({"message": "city added successfully", "id": inserted_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Update an Existing city
@city_bp.route("/update", methods=["POST"])
@protected
def update_city():
    """Update an existing city by CityId."""
    try:
        data = request.get_json()
        city_id=data.get("CityId")
        data.pop("CityId")
        print(city_id)
        print(data)
        updated = City.update_city(city_id, data)
        if updated:
            return jsonify({"message": "city updated successfully"}), 200
        else:
            return jsonify({"error": "city not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Delete a city
@city_bp.route("/delete", methods=["POST"])
@protected
def delete_city():
    """Delete a city by CityId."""
    try:
        data = request.get_json()
        city_id=data.get("CityId")
        deleted = City.delete_city(city_id)
        if deleted:
            return jsonify({"message": "city deleted successfully"}), 200
        else:
            return jsonify({"error": "city not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
