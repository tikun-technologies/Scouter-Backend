# import concurrent
# from models.activity_model import Activity
from pymongo import UpdateOne
from config.db_config import ACTIVITY_COLLECTION, USER_COLLECTION,USER_DEVICE_COLLECTION,PLACE_COLLECTION
import requests

# fetch_url = "https://portal.maiden-ai.com/api/v1/cube/Scouter Galactic Pvt Ltd/night life/scoutermap/Place/list"
# headers = {
#     "Content-Type": "application/json",
#     "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJVc2VySWQiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJEZXZpY2VJZCI6IjFCREVEODlCLUI1OTAtNEYwQy1BRTc0LUMyODY0OTRFMDNEOCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjExLzIxLzIwMjQgMDk6MzQ6MDgiLCJuYmYiOjE3MzIxODE2NDgsImV4cCI6MTc2MzcxNzY0OCwiaWF0IjoxNzMyMTgxNjQ4fQ.ycA3jokPX3G46fZk4toGNT5oTfDepv1NLfSNMK1ka3Y"
# }
# payload = {
#     "pageSize":1000000000,
# }

# response = requests.post(fetch_url, json=payload, headers=headers)
# print(len(response.json()['data']))
# # def insert_place_worker(place_data):
# #     # print(place_data)
# #     try:
        
# #         place_data["_id"] = place_data["DeviceId"]
# #         place_data["UserId"] = place_data["DeviceUserId"]
# #         aa=USER_DEVICE_COLLECTION.insert_one(place_data)
# #         print(aa.inserted_id)
# #         # return 
# #     except Exception as e:
# #         return f"Error inserting "

# # with concurrent.futures.ThreadPoolExecutor(max_workers=10000) as executor:
# #     results = list(executor.map(insert_place_worker, response.json()["data"]))

# # print("All inserts completed!")


# for place_data in response.json()["data"]:
#     print(place_data)
#     place_data["_id"] = place_data["DeviceId"]  # Use DeviceId as the unique identifier
#     place_data["UserId"] = place_data.get("DeviceUserId", None)

#     # ✅ Update if exists, Insert if new
#     USER_DEVICE_COLLECTION.update_one(
#         {"_id": place_data["_id"]}, 
#         {"$set": place_data}, 
#         upsert=True
#     )
  
   
    
    
    
users=USER_COLLECTION.delete_many({})
print(users)
    
    
# ACTIVITY_COLLECTION.update_many({},  # Filter: Select documents where LikeCount is 0
#     {"$set": {"LikeCount": 0}} )
# # aa=list(USER_DEVICE_COLLECTION.find({}))
# # print(aa)
# aaaaa=[]
# for d in response.json()["data"]:
#     d["_id"]=d["PlaceId"] 
#     aaaaa.append(d)

# operations = [
#     UpdateOne({"PlaceId": doc["PlaceId"]}, {"$setOnInsert": doc}, upsert=True)
#     for doc in aaaaa
# ]




# # ✅ Execute bulk operation
# if operations:
#     PLACE_COLLECTION.bulk_write(operations)