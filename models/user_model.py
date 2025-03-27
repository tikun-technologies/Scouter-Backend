from datetime import datetime
from config.db_config import USER_COLLECTION
from marshmallow import Schema,fields,validate


class userSchema(Schema):
  
    _id = fields.Str(required=True)  # _id will be the same as userId
    UserId = fields.Str(required=True)
    CreatedBy = fields.Str(allow_none=True)
    ModifiedBy = fields.Str(allow_none=True)
    CreatedDate = fields.DateTime(default=datetime.utcnow())
    ModifiedDate = fields.DateTime(default=datetime.utcnow())
    Name = fields.Str()
    ProfileImage = fields.Str(allow_none=True)
    Age = fields.Int(allow_none=True)
    Sex = fields.Str(allow_none=True)
    Race = fields.Str(allow_none=True)
    Interests = fields.Str(allow_none=True)
    Latitude = fields.Float(allow_none=True)
    Longitude = fields.Float(allow_none=True)
    EmojiFlagUniCode = fields.Str(allow_none=True)
    EmojiPartyAnimalUniCode = fields.Str(allow_none=True)
    NativePlace = fields.Str(allow_none=True)
    isStatusOpen = fields.Bool(allow_none=True)
    UserDescription = fields.Str(allow_none=True)
    userLevel = fields.Int(allow_none=True)
    CountryCode = fields.Str(allow_none=True)
    Phone = fields.Str(allow_none=True)
    FullName = fields.Str(allow_none=True)
    Email = fields.Email(allow_none=True)
    DateofBirth = fields.DateTime(allow_none=True)
    IsArchived = fields.Bool(allow_none=True)
    BatchName = fields.Str(allow_none=True)
    InstagramBusiness = fields.Str(allow_none=True)
    ExternalURl = fields.Str(allow_none=True)
    InstagramPk = fields.Str(allow_none=True)
    InstagramVerified = fields.Bool(allow_none=True)
    InstagramFollowerCount = fields.Int(allow_none=True)
    InstagramFollowingCount = fields.Int(allow_none=True)
    MediaCount = fields.Int(allow_none=True)
    IsBlocked = fields.Bool(allow_none=True)
    UserName = fields.Str(allow_none=True)
    Ethnicity = fields.Str(allow_none=True)
    Bio = fields.Str(allow_none=True)
    CityId = fields.Str(allow_none=True)
    IsActive = fields.Bool(allow_none=True)
    MigratedProfileImage = fields.Str(allow_none=True)
    DeviceId = fields.Str(allow_none=True)
    PlaceId = fields.Str(allow_none=True)
    favourite = fields.Dict(required=True)






class User:
    def get_users( filters, page, page_size):
        """Fetches users with applied filters and pagination."""
        skip = (page - 1) * page_size
        data = list(USER_COLLECTION.find(filters).skip(skip).limit(page_size))
        total = USER_COLLECTION.count_documents(filters)
        return {
            "data": data,
            "page": page,
            "pageSize": page_size,
            "total": total
        }

    @staticmethod
    def insert_user( data):
        """Inserts a new user document."""
        schema = userSchema()
        main_data=schema.load(data)
        errors = schema.validate(data)
        if errors:
            return {"error": errors}
        result = USER_COLLECTION.insert_one(main_data)
        return data

    @staticmethod
    def update_user( user_id, update_data):
        """Updates an existing user document."""
        result = USER_COLLECTION.update_one({"UserId": user_id}, {"$set": update_data})
        print(result)
        return True

    @staticmethod
    def delete_user( user_id):
        """Deletes a user document."""
        result = USER_COLLECTION.delete_one({"UserId": user_id})
        return result.deleted_count > 0
