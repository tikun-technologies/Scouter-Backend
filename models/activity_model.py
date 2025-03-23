from datetime import  datetime
from config.db_config import ACTIVITY_COLLECTION
from marshmallow import Schema,fields,validate


class ActivitySchema(Schema):
    _id = fields.Str() 
    ActivityId = fields.Str(required=True)
    CreatedBy = fields.Str()
    ModifiedBy = fields.Str()
    CreatedDate = fields.DateTime(default=datetime.utcnow)
    ModifiedDate = fields.DateTime(default=datetime.utcnow)
    ActivityType = fields.Str(required=True) 
    AttachmentType = fields.Str(allow_none=True)
    ActivityDate = fields.DateTime(allow_none=True)
    StartTime = fields.Str(allow_none=True)
    EndTime = fields.Str(allow_none=True)
    Title = fields.Str()
    Description = fields.Str()
    InLocation = fields.Bool()
    TagLocation = fields.Str(allow_none=True)
    LikeCount = fields.Int()
    DisLikeCount = fields.Int(allow_none=True)
    AttachmentUrl = fields.Str()
    ThumbnailUrl = fields.Str(allow_none=True)
    Emoji = fields.Str(allow_none=True)
    Hashtag1 = fields.Str(allow_none=True)
    Hashtag2 = fields.Str(allow_none=True)
    Hashtag3 = fields.Str(allow_none=True)
    Hashtag4 = fields.Str(allow_none=True)
    Hashtag5 = fields.Str(allow_none=True)
    BatchName = fields.Str()
    Hide = fields.Bool(allow_none=True)
    MigratedUrl = fields.Str(allow_none=True)
    MigratedDate = fields.DateTime(allow_none=True)
    IsNeeded = fields.Bool(allow_none=True)
    IsAvailable = fields.Bool(allow_none=True)
    Latitude = fields.Float()
    Longitude = fields.Float()
    PlaceId = fields.Str()
    CityId = fields.Str()
    MinPrice = fields.Float(allow_none=True)
    MaxPrice = fields.Float(allow_none=True)
    Address = fields.Str(allow_none=True)
    Url = fields.Str(allow_none=True)
    MinimumTicketPrice = fields.Float(allow_none=True)
    IsSoldOut = fields.Bool(allow_none=True)
    FullDescription = fields.Str(allow_none=True)
    TicketsUrl = fields.Str(allow_none=True)
    MaximumTicketPrice = fields.Float(allow_none=True)
    Currency = fields.Str(allow_none=True)
    InstagramPk = fields.Str(allow_none=True)
    IsFlagged = fields.Bool(allow_none=True)
    FlaggedUsers = fields.List(fields.Str(), allow_none=True)
    ViewCount = fields.Int(allow_none=True)
    ViewedUsers = fields.List(fields.Str(), allow_none=True)
    LikeCount = fields.Int(allow_none=True)
    LikedUsers = fields.List(fields.Str(), allow_none=True)
    IsLiked = fields.Bool( allow_none=True)
    InstaShortCode = fields.Str(allow_none=True)
    Region = fields.Str(allow_none=True)
    MigratedThumbnailUrl = fields.Str(allow_none=True)
    
    






class Activity:
    def get_activity( filters, page, page_size):
        """Fetches activity with applied filters and pagination."""
        skip = (page - 1) * page_size
        data = list(ACTIVITY_COLLECTION.find(filters).skip(skip).limit(page_size))
        total = ACTIVITY_COLLECTION.count_documents(filters)
        return {
            "success": True,
            "data": data,
            "page": page,
            "pageSize": page_size,
            "total": total
        }

    @staticmethod
    def insert_activity( data):
        """Inserts a new place document."""
        schema = ActivitySchema()
        errors = schema.validate(data)
        if errors:
            return {"error": errors}
        result = ACTIVITY_COLLECTION.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def update_activity( activity_id, update_data):
        """Updates an existing place document."""
        result = ACTIVITY_COLLECTION.update_one({"ActivityId": activity_id}, {"$set": update_data})
        print(result)
        return result.modified_count > 0

    @staticmethod
    def delete_activity( activity_id):
        """Deletes a place document."""
        result = ACTIVITY_COLLECTION.delete_one({"ActivityId": activity_id})
        return result.deleted_count > 0
