import concurrent
from models.activity_model import Activity
from config.db_config import ACTIVITY_COLLECTION
import requests

fetch_url = "https://portal.maiden-ai.com/api/v1/cube/Scouter Galactic Pvt Ltd/night life/scoutermap/Activity/list"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJVc2VySWQiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJEZXZpY2VJZCI6IjFCREVEODlCLUI1OTAtNEYwQy1BRTc0LUMyODY0OTRFMDNEOCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjExLzIxLzIwMjQgMDk6MzQ6MDgiLCJuYmYiOjE3MzIxODE2NDgsImV4cCI6MTc2MzcxNzY0OCwiaWF0IjoxNzMyMTgxNjQ4fQ.ycA3jokPX3G46fZk4toGNT5oTfDepv1NLfSNMK1ka3Y"
}
payload = {
    "pageSize":1000000000,
}

response = requests.post(fetch_url, json=payload, headers=headers)
print(len(response.json()['data']))
def insert_place_worker(place_data):
    # print(place_data)
    try:
        place_data["_id"] = place_data["ActivityId"]
        place_data["LikedUsers"]=[]
        place_data["FlaggedUsers"]=[]
        place_data["ViewedUsers"]=[]
        return ACTIVITY_COLLECTION.insert_one(place_data)
    except Exception as e:
        return f"Error inserting {place_data['ActivityId']}: {str(e)}"

with concurrent.futures.ThreadPoolExecutor(max_workers=10000) as executor:
    results = list(executor.map(insert_place_worker, response.json()["data"]))

print("All inserts completed!")


    
# ACTIVITY_COLLECTION.delete_many({})