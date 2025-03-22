import requests
from models.city_model import City
# Step 1: Fetch city data from old server
fetch_url = "https://portal.maiden-ai.com/api/v1/cube/Scouter Galactic Pvt Ltd/night life/scoutermap/City/list"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJVc2VySWQiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJEZXZpY2VJZCI6IjFCREVEODlCLUI1OTAtNEYwQy1BRTc0LUMyODY0OTRFMDNEOCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjExLzIxLzIwMjQgMDk6MzQ6MDgiLCJuYmYiOjE3MzIxODE2NDgsImV4cCI6MTc2MzcxNzY0OCwiaWF0IjoxNzMyMTgxNjQ4fQ.ycA3jokPX3G46fZk4toGNT5oTfDepv1NLfSNMK1ka3Y"
}
payload = {
    "filterInfo": [
        {
            "filterBy": "IsScouter",
            "filterTerm": "1"
        }
    ]
}

response = requests.post(fetch_url, json=payload, headers=headers)

for i in response.json()["data"]:
    print(i)
    i["_id"]=i["CityId"]
    aa=City.insert_city(i)
    print(aa)