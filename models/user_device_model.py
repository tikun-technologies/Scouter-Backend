from datetime import datetime
from config.db_config import USER_DEVICE_COLLECTION
from marshmallow import Schema,fields,validate


class User_Device_Schema(Schema):
  
    _id = fields.Str()  # _id will be the same as user_deviceId
    DeviceId = fields.Str(required=True)
    # CreatedBy = fields.Str(required=True)
    # ModifiedBy = fields.Str(required=True)
    # CreatedDate = fields.DateTime(required=True)
    # ModifiedDate = fields.DateTime(required=True)
    DeviceToken = fields.Str(allow_none=True)
    Language = fields.Str(allow_none=True)
    IsDeviceAllowed = fields.Bool(allow_none=True)
    DeviceUUID = fields.Str(allow_none=True)
    DeviceName = fields.Str(allow_none=True)
    DeviceType = fields.Str(allow_none=True)
    DeviceOSVersion = fields.Str(allow_none=True)
    AppName = fields.Str(allow_none=True)
    AppVersion = fields.Str(allow_none=True)
    IsArchive = fields.Bool(allow_none=True)
    ArchiveDate = fields.DateTime(allow_none=True)
    UserDeviceNotifGuid = fields.Str(allow_none=True)
    NotifRegistrationId = fields.Str(allow_none=True)
    UserId = fields.Str(allow_none=True)
    IsActive = fields.Bool(allow_none=True)






class User_Device:
    def get_user_devices( filters, page, page_size):
        """Fetches user_devices with applied filters and pagination."""
        skip = (page - 1) * page_size
        data = list(USER_DEVICE_COLLECTION.find(filters).skip(skip).limit(page_size))
        total = USER_DEVICE_COLLECTION.count_documents(filters)
        return {
            "data": data,
            "page": page,
            "pageSize": page_size,
            "total": total
        }

    @staticmethod
    def insert_user_device( data):
        """Inserts a new user_device document."""
        schema = User_Device_Schema()
        errors = schema.validate(data)
        if errors:
            return {"error": errors}
        result = USER_DEVICE_COLLECTION.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def update_or_insert_user_device(user_device_id, update_data):
        """Updates an existing user_device document or inserts a new one if not found."""
        schema = User_Device_Schema()
        errors = schema.validate(update_data)

        if errors:
            return {"error": errors}, 400

        # Ensure we track modification date
        # Use upsert=True to update if exists, insert if not
        result = USER_DEVICE_COLLECTION.update_one(
            {"DeviceId": user_device_id},
            {"$set": update_data},
            upsert=True
        )
        update_data["DeviceId"]=user_device_id
        if result.matched_count > 0:
            return update_data
        else:
            return update_data

    @staticmethod
    def delete_user_device( user_device_id):
        """Deletes a user_device document."""
        result = USER_DEVICE_COLLECTION.delete_one({"user_deviceId": user_device_id})
        return result.deleted_count > 0
