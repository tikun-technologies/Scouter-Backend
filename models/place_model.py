from datetime import datetime
from config.db_config import PLACE_COLLECTION, USER_COLLECTION
from marshmallow import Schema, fields, validate
from pymongo import UpdateOne


class PlaceSchema(Schema):
    _id = fields.Str(required=True)
    CreatedBy = fields.Str()
    ModifiedBy = fields.Str()
    CreatedDate = fields.DateTime(lambda: datetime.utcnow())
    ModifiedDate = fields.DateTime(lambda: datetime.utcnow())
    PlaceId = fields.Str(required=True)
    CityId = fields.Str(required=True)
    PlaceName = fields.Str(required=True)
    Country = fields.Str(required=True)
    Address = fields.Str(required=True)
    Zipcode = fields.Int()
    Latitude = fields.Float(required=True)
    Longitude = fields.Float(required=True)
    location = fields.Dict(required=True)
    PlaceType = fields.Str()

    BusyHoursSun = fields.Str()
    BusyHoursMon = fields.Str()
    BusyHoursTue = fields.Str()
    BusyHoursWed = fields.Str()
    BusyHoursThu = fields.Str()
    BusyHoursFri = fields.Str()
    BusyHoursSat = fields.Str()

    RaceWhite = fields.Int()
    RaceBlack = fields.Int()
    RaceAsian = fields.Int()
    RaceLatino = fields.Int()
    RaceIndian = fields.Int()

    GenderMale = fields.Int()
    GenderFemale = fields.Int()
    GenderOthers = fields.Int()

    InterestGay = fields.Int()
    InterestStraight = fields.Int()
    InterestBisexual = fields.Int()

    PriceRange = fields.Str()
    PhoneNumber = fields.Str()
    shortcode = fields.Str(allow_none=True)
    GooglePlaceName = fields.Str(allow_none=True)
    Timewait = fields.Str(allow_none=True)
    CurrentPopularity = fields.Int(allow_none=True)
    TimeSpent = fields.Str(allow_none=True)
    GoogleMapLocation = fields.Str(allow_none=True)
    FacebookLink = fields.Str(allow_none=True)
    TimeZone = fields.Str(allow_none=True)
    Neighborhood = fields.Str(allow_none=True)
    AverageTimeSpent = fields.Str(allow_none=True)
    BatchName = fields.Str(allow_none=True)
    InstagramHandle = fields.Str(allow_none=True)
    InstagramLocation = fields.Str()
    MigratedImages = fields.Str(allow_none=True)
    ImagesUrl = fields.Str(allow_none=True)
    GooglePlaceImage = fields.Str(allow_none=True)
    CurrentPopularityStatus = fields.Str(allow_none=True)
    Rating = fields.Float(allow_none=True)
    Rating_N = fields.Float(allow_none=True)
    StartTime = fields.Str(allow_none=True)
    EndTime = fields.Str(allow_none=True)
    OpeningHours = fields.Str(allow_none=True)
    Description = fields.Str(allow_none=True)
    Reviews = fields.Str(allow_none=True)
    ReviewsID = fields.Str(allow_none=True)
    ReviwsID = fields.Str(allow_none=True)
    InstagramHandlePk = fields.Str(allow_none=True)
    PopularityType = fields.Str(allow_none=True)
    OpeningStart = fields.Str(allow_none=True)
    OpeningEnd = fields.Str(allow_none=True)


class Place:
    def get_places(filters, user_id, latitude, longitude,max_distance, page, page_size):
        """Fetches places with applied filters and pagination."""
        user = USER_COLLECTION.find_one({"UserId": user_id})
        print(user)
        # print(user["favourite"]["favouritePlace"])
        skip = (page - 1) * page_size
        pipeline = [
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [longitude, latitude],
                    },  # User's current location
                    "distanceField": "distance",  # Field to store calculated distance
                    "spherical": True,  # Use spherical calculation for real-world accuracy
                    "key": "location",
                    "maxDistance": int(max_distance)*1000# Specify the location field
                }
            },
            {"$match": filters},  # Apply filters after distance calculation
            {
                "$addFields": {
                    "IsFavourite": {
                        "$in": ["$PlaceId", user["favourite"]["favouritePlace"]]
                    }  # Check if PlaceId is in the user's favourite list
                }
            },
            {
                "$sort": {"distance": 1, "CurrentPopularity": -1}
            },  # ✅ Sort: Nearest first, then most popular
            {"$skip": skip},  # Apply pagination
            {"$limit": page_size},  # Apply page size limit
        ]
        data = list(PLACE_COLLECTION.aggregate(pipeline))
        total = PLACE_COLLECTION.count_documents({
    "location": {
        "$geoWithin": {
            "$centerSphere": [[longitude, latitude], (int(max_distance) * 1000) / 6371000]  # Convert max_distance to radians
        }
    },
    **filters  # Apply additional filters
})
        return {
            "success": True,
            "data": data,
            "page": page,
            "pageSize": page_size,
            "total": total,
        }

    @staticmethod
    def insert_place(data):
        """Inserts a new place document."""
        schema = PlaceSchema()
        main_data = schema.load(data)
        errors = schema.validate(data)
        if errors:
            return {"error": errors}
        result = PLACE_COLLECTION.insert_one(main_data)
        return str(result.inserted_id)

    @staticmethod
    def update_place(place_id, update_data):
        """Updates an existing place document."""
        result = PLACE_COLLECTION.update_one(
            {"PlaceId": place_id}, {"$set": update_data}
        )
        print(result)
        return result.modified_count > 0

    @staticmethod
    def update_many(update_data):
        """Updates an existing place document."""
        # Create a list of update operations
        bulk_updates = []

        for item in update_data:
            place_id = item.get("PlaceId")
            current_popularity = item.get("Currentpopularity")
            if place_id and current_popularity is not None:
                bulk_updates.append(
                    UpdateOne(
                        {"PlaceId": place_id},  # Filter by PlaceId
                        {
                            "$set": {"CurrentPopularity": current_popularity}
                        },  # Update field
                    )
                )
        # print(bulk_updates)
        if bulk_updates:
            result = PLACE_COLLECTION.bulk_write(bulk_updates)
            print(result)
            return result.modified_count  # Number of documents updated
        return 0

    @staticmethod
    def delete_place(place_id):
        """Deletes a place document."""
        result = PLACE_COLLECTION.delete_one({"PlaceId": place_id})
        return result.deleted_count > 0
