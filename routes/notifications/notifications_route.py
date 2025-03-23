from datetime import datetime, timedelta
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from config.db_config import NOTIFICATION_COLLECTION, USER_DEVICE_COLLECTION, USER_LOCATION_COLLECTION
from models.notification_model import Notification
from utils.helper import apply_filters, protected, send_notifications_to_all, send_push_notification_user, upload_to_azure


notification_bp = Blueprint("notification", __name__)


@notification_bp.route("/list", methods=["POST"])
@protected
def get_notifications():
    """Fetch notifications using filters and pagination."""
    try:
        data = request.get_json()
        filters = apply_filters({}, data)
        page = int(data.get("page", 1))
        page_size = int(data.get("pageSize", 10))
        result = Notification.get_user_notification(filters, page, page_size)
        return jsonify(result), 200
       
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# ✅ Create a New notification
@notification_bp.route("/insert", methods=["POST"])
@protected
def create_notification():
    """Insert a new notification into the database."""
    try:
        notification_data = request.get_json()
        _id = str(uuid.uuid4())
        notification_data["AppNotificationId"] = _id
        notification_data["_id"] = _id
        notification_data["CreatedBy"] = get_jwt_identity()
        inserted_id = Notification.insert_user_notification(notification_data)
        return jsonify({"message": "notification added successfully", "id": inserted_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Update an Existing notification
@notification_bp.route("/update", methods=["POST"])
@protected
def update_notification():
    """Update an existing notification by notificationId."""
    try:
        data = request.get_json()
        notification_id = data.get("AppNotificationId")
        data.pop("AppNotificationId")
        print(notification_id)
        print(data)
        
        updated = Notification.update_or_insert_user_notification(notification_id, data)
        if updated:
            return jsonify({"message": "notification updated successfully"}), 200
        else:
            return jsonify({"error": "notification not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Delete a notification
@notification_bp.route("/delete", methods=["POST"])
@protected
def delete_notification(notification_id):
    """Delete a notification by notificationId."""
    try:
        data = request.get_json()
        notification_id = data.get("AppNotificationId")
        deleted = Notification.delete_user_notification(notification_id)
        if deleted:
            return jsonify({"message": "notification deleted successfully"}), 200
        else:
            return jsonify({"error": "notification not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500





@notification_bp.route("/user-notification-count", methods=["POST"])
@protected   
def get_user_notifications_count():
    data = request.get_json()
    user_id=data.get("UserId")
    count=NOTIFICATION_COLLECTION.count_documents({"UserId":user_id})
    return jsonify({
        "success":True,
        "data":{
            "Count":count
        }
    })
    
    
@notification_bp.route("/send-notification-user", methods=["POST"])
@protected   
def send_user_notifications():
    data = request.get_json()
    title = data.get("Title", "Notification")
    message = data.get("Message", "You have a new notification")
    image_url = data.get("Image_url", None)
    place_id = data.get("PlaceId", None)  # Custom data
    user_id = data.get("UserId", None)  # Custom data
    # days=data.get("Days",None)
    print(data)
    device = USER_DEVICE_COLLECTION.find_one(
    {"UserId": user_id},  # Filter by active user
    {"_id": 0, "DeviceToken": 1}  # Only return DeviceToken 
    )
    devic=device["DeviceToken"]
    print(devic)
    try:
        
        res=send_push_notification_user(title,message,devic,image_url,place_id)
        print(res)
        _id=str(uuid.uuid4())
        data["_id"]=_id
        data["AppNotificationId"]=_id
        if image_url:
            data["ImageUrl"]=upload_to_azure(image_url,'image')
        print(data)
        notify=Notification.insert_user_notification(data)
        res["AppNotificationId"]=notify
        return{
        "success":True,
        "data":res
        }
    except Exception as error:
        return {
        "success":False,
        "message":error
        }



@notification_bp.route("/send-notification-user-visited-place", methods=["POST"])
@protected   
def get_user_notifications_viewed_place():       
          
    data = request.get_json()
    title = data.get("Title", "Notification")
    message = data.get("Message", "You have a new notification")
    image_url = data.get("Image_url", None)
    place_id = data.get("PlaceId", None)  # Custom data
    days = data.get("Days", None)  # Number of days filter

    # Calculate the start date (X days ago)
    if days:
        start_date = datetime.utcnow() - timedelta(days=int(days))
    else:
        start_date = None  # No filter if `days` is None

    # Query with `CreatedDate` filter if days is provided
    query = {"PlaceId": place_id}
    if start_date:
        query["CreatedDate"] = {"$gte": start_date}  # ✅ Only fetch users created in the last X days

    users = USER_LOCATION_COLLECTION.find(
        query, 
        {"_id": 0, "UserId": 1}
        )# ✅ Return only UserId
    user_ids = [user["UserId"] for user in users if "UserId" in user]  # Extract UserIds

    if not user_ids:
        return {"success": False, "error": "No users found in this place"}

    # Step 2️⃣: Find Device Tokens for these UserIds from `UserDevice`
    devices = USER_DEVICE_COLLECTION.find(
        {"UserId": {"$in": user_ids}, "IsActive": True},  # Only active devices
        {"_id": 0, "DeviceToken": 1}  # Fetch only DeviceToken
    )
        # Step 4️⃣: Insert Notifications into `Notifications` Collection
    try:
        res=send_notifications_to_all(title,message,[token for token in devices['DeviceToken']],image_url,place_id)
        notification_records = []
        for user_id in user_ids:
            _id=str(uuid.uuid4())
            data["_id"]=_id,
            data["AppNotificationId"]=_id
            data["UserId"]=user_id
            if image_url:
                data["ImageUrl"]=upload_to_azure(image_url,'image')
            notification_records.append(data)
        if notification_records:
            inserted_ids =NOTIFICATION_COLLECTION.insert_many(notification_records)
            res["AppNotificationId"]=inserted_ids.inserted_ids
            return{
            "success":True,
            "data":res
        }
    except Exception as error:
        return jsonify({
        "success":False,
        "message":error
        }),500

