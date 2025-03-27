from datetime import datetime
from config.db_config import USER_LOCATION_COLLECTION
from marshmallow import Schema,fields,validate


  
class UserLocationSchema(Schema):
    _id=fields.Str(required=True)
    UserLocationId = fields.Str(required=True)
    CreatedBy = fields.Str()
    ModifiedBy = fields.Str()
    CreatedDate = fields.DateTime(missing=lambda: datetime.utcnow())
    ModifiedDate = fields.DateTime(missing=lambda: datetime.utcnow())
    Latitude = fields.Float(required=True)
    Longitude = fields.Float(required=True)
    CityId = fields.UUID(required=True)
    PlaceId = fields.UUID(allow_none=True) 






class User_Location:
    def get_user_locations( filters, page, page_size):
        """Fetches user_devices with applied filters and pagination."""
        skip = (page - 1) * page_size
        data = list(USER_LOCATION_COLLECTION.find(filters).skip(skip).limit(page_size))
        total = USER_LOCATION_COLLECTION.count_documents(filters)
        return {
            "data": data,
            "page": page,
            "pageSize": page_size,
            "total": total
        }

    @staticmethod
    def insert_user_location( data):
        """Inserts a new user_device document."""
        schema = UserLocationSchema()
        main_data=schema.load(data)
        errors = schema.validate(data)
        if errors:
            return {"error": errors}
        result = USER_LOCATION_COLLECTION.insert_one(main_data)
        return str(result.inserted_id)

    @staticmethod
    def update_or_insert_user_location(user_device_id, update_data):
        """Updates an existing user_device document or inserts a new one if not found."""
        schema = UserLocationSchema()
        errors = schema.validate(update_data)

        if errors:
            return {"error": errors}, 400

        # Ensure we track modification date
        # Use upsert=True to update if exists, insert if not
        result = USER_LOCATION_COLLECTION.update_one(
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
        result = USER_LOCATION_COLLECTION.delete_one({"user_deviceId": user_device_id})
        return result.deleted_count > 0
