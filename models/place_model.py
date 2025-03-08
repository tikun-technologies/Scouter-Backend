from config.db_config import PLACE_COLLECTION
from marshmallow import Schema,fields,validate
from pymongo import UpdateOne


class PlaceSchema(Schema):
    _id=fields.Str(required=True)
    CreatedBy = fields.Str()
    ModifiedBy = fields.Str()
    CreatedDate = fields.DateTime()
    ModifiedDate = fields.DateTime()
    PlaceId=fields.Str(required=True)
    CityId = fields.Str(required=True)
    PlaceName = fields.Str(required=True)
    Country = fields.Str(required=True)
    Address = fields.Str(required=True)
    Zipcode = fields.Int()
    Latitude = fields.Float(required=True)
    Longitude = fields.Float(required=True)
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
    GooglePlaceName = fields.Str()
    Timewait = fields.Str(allow_none=True)
    CurrentPopularity = fields.Int()
    TimeSpent = fields.Str()
    GoogleMapLocation = fields.Str()
    FacebookLink = fields.Str()
    TimeZone = fields.Str()
    Neighborhood = fields.Str()
    AverageTimeSpent = fields.Str()
    BatchName = fields.Str(allow_none=True)
    InstagramHandle = fields.Str()
    InstagramLocation = fields.Str()
    MigratedImages = fields.Str(allow_none=True)
    ImagesUrl = fields.Str()
    GooglePlaceImage = fields.Str()
    CurrentPopularityStatus = fields.Str()
    Rating = fields.Float()
    Rating_N = fields.Float()
    StartTime = fields.Str(allow_none=True)
    EndTime = fields.Str(allow_none=True)
    OpeningHours = fields.Str()
    Description = fields.Str()
    Reviews = fields.Str()
    ReviewsID = fields.Str()
    InstagramHandlePk = fields.Str(allow_none=True)
    PopularityType = fields.Str()
    OpeningStart = fields.Str()
    OpeningEnd = fields.Str()
    
    






class Place:
    def get_places( filters, page, page_size):
        """Fetches places with applied filters and pagination."""
        skip = (page - 1) * page_size
        data = list(PLACE_COLLECTION.find(filters).skip(skip).limit(page_size))
        total = PLACE_COLLECTION.count_documents(filters)
        return {
            "data": data,
            "page": page,
            "pageSize": page_size,
            "total": total
        }

    @staticmethod
    def insert_place( data):
        """Inserts a new place document."""
        schema = PlaceSchema()
        errors = schema.validate(data)
        if errors:
            return {"error": errors}
        result = PLACE_COLLECTION.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def update_place( place_id, update_data):
        """Updates an existing place document."""
        result = PLACE_COLLECTION.update_one({"PlaceId": place_id}, {"$set": update_data})
        print(result)
        return result.modified_count > 0
    @staticmethod
    def update_many(update_data):
        """Updates an existing place document."""
        # Create a list of update operations
        bulk_updates = []
        
        for item in update_data:
            place_id = item.get("PlaceId")
            current_popularity = item.get("CurrentPopularity")
            if place_id and current_popularity is not None:
                bulk_updates.append(
                    UpdateOne(
                        {"PlaceId": place_id},  # Filter by PlaceId
                        {"$set": {"CurrentPopularity": current_popularity}}  # Update field
                    )
                )

        if bulk_updates:
            result = PLACE_COLLECTION.bulk_write(bulk_updates)
            return result.modified_count  # Number of documents updated
        return 0

    @staticmethod
    def delete_place( place_id):
        """Deletes a place document."""
        result = PLACE_COLLECTION.delete_one({"PlaceId": place_id})
        return result.deleted_count > 0
