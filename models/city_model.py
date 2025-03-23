from datetime import datetime
from config.db_config import CITY_COLLECTION
from marshmallow import Schema,fields,validate


class CitySchema(Schema):
  
    _id = fields.Str()  # _id will be the same as CityId
    CityId = fields.Str(required=True)
    CreatedBy = fields.Str()
    ModifiedBy = fields.Str()
    CreatedDate = fields.DateTime(default=datetime.utcnow)
    ModifiedDate = fields.DateTime(default=datetime.utcnow)
    CityName = fields.Str(required=True)
    Country = fields.Str(required=True)
    PolyLatDiff = fields.Float(allow_none=True)
    PolyLongDiff = fields.Float(allow_none=True)
    Latitude = fields.Float(required=True)
    Longitude = fields.Float(required=True)
    CityState = fields.Str(allow_none=True)
    CityRankInTheCountry = fields.Int(allow_none=True)
    TimeZone = fields.Str(allow_none=True)
    Abbreviation = fields.Str(allow_none=True)
    cityCount = fields.Int(allow_none=True)
    IsScouter = fields.Bool()
    IsPopular = fields.Bool(allow_none=True)
    PlaceCount=fields.Int(allow_none=True)
    






class City:
    def get_citys( filters, page, page_size):
        """Fetches citys with applied filters and pagination."""
        skip = (page - 1) * page_size
        data = list(CITY_COLLECTION.find(filters).skip(skip).limit(page_size))
        total = CITY_COLLECTION.count_documents(filters)
        return {
            "data": data,
            "page": page,
            "pageSize": page_size,
            "total": total
        }

    @staticmethod
    def insert_city( data):
        """Inserts a new city document."""
        schema = CitySchema()
        errors = schema.validate(data)
        
        if errors:
            print(errors)
            return {"error": errors}
        result = CITY_COLLECTION.insert_one(data)
   
        return str(result.inserted_id)

    @staticmethod
    def update_city( city_id, update_data):
        """Updates an existing city document."""
        result = CITY_COLLECTION.update_one({"CityId": city_id}, {"$set": update_data})
        print(result)
        return result.modified_count > 0

    @staticmethod
    def delete_city( city_id):
        """Deletes a city document."""
        result = CITY_COLLECTION.delete_one({"CityId": city_id})
        return result.deleted_count > 0
