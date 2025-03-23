from pymongo import MongoClient,GEOSPHERE

uri = "mongodb+srv://dlovej009:Dheeraj2006@scouterdb.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
client = MongoClient(uri)
db = client['Scouter']
USER_COLLECTION = db['USER']
USER_DEVICE_COLLECTION = db['USER_DEVICE']
USER_LOCATION_COLLECTION = db['USER_LOCATION']
PLACE_COLLECTION = db['PLACES']
CITY_COLLECTION = db['CITY']
ACTIVITY_COLLECTION = db['ACTIVITY']
NOTIFICATION_COLLECTION = db['NOTIFICATION']
PLACE_COLLECTION.create_index([("location", GEOSPHERE)])
print("connected to db ")