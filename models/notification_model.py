from datetime import datetime
from marshmallow import Schema, fields
from config.db_config import NOTIFICATION_COLLECTION
class NotificationSchema(Schema):
    _id=fields.Str(required=True)
    AppNotificationId = fields.Str(required=True)  # Unique ID for the notification
    CreatedBy = fields.Str(allow_none=True)  
    ModifiedBy = fields.Str(allow_none=True)
    CreatedDate = fields.DateTime(default=datetime.utcnow)
    ModifiedDate = fields.DateTime(default=datetime.utcnow)
    IsRead = fields.Bool(default=False)
    UserId = fields.Str(allow_none=True)
    RepliedUserId = fields.Str(allow_none=True)
    Title = fields.Str(required=True)
    Message = fields.Str(required=True)
    AppNotificationType = fields.Str(allow_none=True)  
    IsReceived = fields.Bool(default=False)
    IsClicked = fields.Bool(default=False)
    RecordId = fields.Str(allow_none=True)
    RecordType = fields.Str(allow_none=True)
    PlaceId = fields.Str(allow_none=True)
    EventId = fields.Str(allow_none=True)
    OfferId = fields.Str(allow_none=True)
    PlaceName = fields.Str(allow_none=True)
    Latitude = fields.Float(allow_none=True)
    Longitude = fields.Float(allow_none=True)
    OpeningHours = fields.Str(allow_none=True)
    ImageUrl = fields.Str(allow_none=True)
    OpeningStart = fields.Str(allow_none=True)
    OpeningEnd = fields.Str(allow_none=True)





class Notification:
    def get_user_notification( filters, page, page_size):
        """Fetches user_devices with applied filters and pagination."""
        skip = (page - 1) * page_size
        data = list(NOTIFICATION_COLLECTION.find(filters).skip(skip).limit(page_size))
        total = NOTIFICATION_COLLECTION.count_documents(filters)
        return {
            "data": data,
            "page": page,
            "pageSize": page_size,
            "total": total
        }

    @staticmethod
    def insert_user_notification( data):
        """Inserts a new user_device document."""
        schema = NotificationSchema()
        errors = schema.validate(data)
        if errors:
            return {"error": errors}
        result = NOTIFICATION_COLLECTION.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def update_or_insert_user_notification(AppNotificationId, update_data):
        """Updates an existing user_device document or inserts a new one if not found."""
        schema = NotificationSchema()
        errors = schema.validate(update_data)

        if errors:
            return {"error": errors}, 400

        # Ensure we track modification date
        # Use upsert=True to update if exists, insert if not
        result = NOTIFICATION_COLLECTION.update_one(
            {"AppNotificationId": AppNotificationId},
            {"$set": update_data},
            upsert=True
        )
        update_data["AppNotificationId"]=AppNotificationId
        if result.matched_count > 0:
            return update_data
        else:
            return update_data

    @staticmethod
    def delete_user_notification( user_device_id):
        """Deletes a user_device document."""
        result = NOTIFICATION_COLLECTION.delete_one({"user_deviceId": user_device_id})
        return result.deleted_count > 0
