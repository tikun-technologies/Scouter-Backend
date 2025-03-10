from pymongo import MongoClient
uri = "mongodb+srv://dlovej009:Dheeraj2006@cluster0.dnu8vna.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['Scouter']
USER_COLLECTION = db['USER']
USER_DEVICE_COLLECTION = db['USER_DEVICE']
PLACE_COLLECTION = db['PLACES']
CITY_COLLECTION = db['CITY']
ACTIVITY_COLLECTION = db['ACTIVITY']
print("connected to db ")