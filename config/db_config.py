from pymongo import MongoClient,GEOSPHERE
uri = "mongodb+srv://dlovej009:Dheeraj2006@cluster0.dnu8vna.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['Scouter']
USER_COLLECTION = db['USER']
USER_DEVICE_COLLECTION = db['USER_DEVICE']
USER_LOCATION_COLLECTION = db['USER_LOCATION']
PLACE_COLLECTION = db['PLACES']
CITY_COLLECTION = db['CITY']
ACTIVITY_COLLECTION = db['ACTIVITY']
PLACE_COLLECTION.create_index([("location", GEOSPHERE)])
print("connected to db ")