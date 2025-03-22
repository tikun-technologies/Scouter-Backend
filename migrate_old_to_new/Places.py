import concurrent
from models.place_model import Place
import requests

fetch_url = "https://portal.maiden-ai.com/api/v1/cube/Scouter Galactic Pvt Ltd/night life/scoutermap/Place/list"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJVc2VySWQiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJEZXZpY2VJZCI6IjFCREVEODlCLUI1OTAtNEYwQy1BRTc0LUMyODY0OTRFMDNEOCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjExLzIxLzIwMjQgMDk6MzQ6MDgiLCJuYmYiOjE3MzIxODE2NDgsImV4cCI6MTc2MzcxNzY0OCwiaWF0IjoxNzMyMTgxNjQ4fQ.ycA3jokPX3G46fZk4toGNT5oTfDepv1NLfSNMK1ka3Y"
}
payload = {
}

response = requests.post(fetch_url, json=payload, headers=headers)

def insert_place_worker(place_data):
    print(place_data)
    try:
        place_data["_id"] = place_data["PlaceId"]
        place_data["location"] = {
            "type": "Point",
            "coordinates": [float(place_data["Longitude"]), float(place_data["Latitude"])],
        }
        return Place.insert_place(place_data)
    except Exception as e:
        return f"Error inserting {place_data['PlaceId']}: {str(e)}"


  # Use ThreadPoolExecutor to insert places concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
    results = list(executor.map(insert_place_worker, response.json()["data"]))

print("All inserts completed!")

# for i in  response.json()["data"]:
#     i["_id"]=i["PlaceId"]
#     i["location"] = {
#             "type": "Point",
#             "coordinates": [float(i["Longitude"]), float(i["Latitude"])],
#         }
#     aa=Place.insert_place(i)
#     print(aa)
#     break