from concurrent.futures import ThreadPoolExecutor
import math
import uuid
from flask import jsonify
from flask_jwt_extended import  jwt_required
from functools import wraps
from flask_jwt_extended import JWTManager
from azure.storage.blob import BlobServiceClient
import requests
from config.db_config import USER_COLLECTION,ACTIVITY_COLLECTION

import firebase_admin
from firebase_admin import credentials, messaging

# Load Firebase credentials (Replace with the correct path to your JSON file)
cred = credentials.Certificate("config/firebase.json")
firebase_admin.initialize_app(cred)


jwt = JWTManager() 
def apply_filters(filters, filter_data):
    """Applies dynamic filters to a MongoDB query."""
    mongo_query = {}

    if filter_data.get("filterInfo"):
        print("in filterrrrererr")
        for filter_item in filter_data.get("filterInfo"):
            field = filter_item["filterBy"]
            value = filter_item["filterTerm"]
            filter_type = filter_item["filterType"]

            if filter_type == "EQUALS":
                mongo_query[field] = value
            elif filter_type == "CONTAINS":
                mongo_query[field] = {"$regex": value, "$options": "i"}  # Case-insensitive search
            elif filter_type == "GREATER_THAN":
                mongo_query[field] = {"$gt": value}
            elif filter_type == "LESS_THAN":
                mongo_query[field] = {"$lt": value}
                
                
    if filter_data.get("Boundary"):
        boundary=filter_data.get("Boundary")
        lat_min = min(boundary["Latitude1"], boundary["Latitude2"])
        lat_max = max(boundary["Latitude1"], boundary["Latitude2"])
        lon_min = min(boundary["Longitude1"], boundary["Longitude2"])
        lon_max = max(boundary["Longitude1"], boundary["Longitude2"])

        # Query to filter places within boundary
        mongo_query = {
            "Latitude": {"$gte": lat_min, "$lte": lat_max},
            "Longitude": {"$gte": lon_min, "$lte": lon_max}
        }

        
    print(mongo_query)
    return mongo_query

def paginate_query(collection, filters, page, page_size):
    """Handles pagination and returns paginated results."""
    skip = (page - 1) * page_size
    data = list(collection.find(filters).skip(skip).limit(page_size))
    total = collection.count_documents(filters)

    return {
        "data": data,
        "page": page,
        "pageSize": page_size,
        "total": total
    }



def protected(f):
    @wraps(f)
    @jwt_required()
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper




AZURE_STORAGE_CONNECTION_STRING = "BlobEndpoint=https://maidenimageserver.blob.core.windows.net/;QueueEndpoint=https://maidenimageserver.queue.core.windows.net/;FileEndpoint=https://maidenimageserver.file.core.windows.net/;TableEndpoint=https://maidenimageserver.table.core.windows.net/;SharedAccessSignature=sv=2022-11-02&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2077-03-10T01:54:07Z&st=2025-03-09T17:54:07Z&spr=https&sig=5TPMCs%2Bbvls%2BuAkDb9OxGk8V6rtLzAQZLHhsBK7NZlM%3D"
CONTAINER_NAME = "scouter"

blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
def upload_to_azure(file_url,file_type):
    try:
        response = requests.get(file_url, stream=True)
        if response.status_code != 200:
            return {"error": "Failed to download image from URL"}, 400
        # Generate a unique blob name
        blob_name = str(uuid.uuid4()) + f"{".jpg" if file_type=="image" else ".mp4"}"
        # Get blob client
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
        # Upload image content to Azure Blob Storage
        blob_client.upload_blob(response.raw, overwrite=True)
        return f"https://maidenimageserver.blob.core.windows.net/scouter/{blob_name}"
    except Exception as err:
       print(err)
       return None
   
def upload_multiple_files(file_list):
    """Uploads multiple images or videos in parallel using ThreadPoolExecutor."""
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(upload_to_azure, file, "image"): file for file in file_list}
        for future in futures:
            results.append(future.result())
    print(results)
    return results



def find_closest_place(collection, lat, lon, max_distance=30):
    """
    Finds the exact place first.
    If not found, finds the nearest place within max_distance meters.
    If no place is found within max_distance, returns None.
    """
    # 🔹 Step 1: Check if there's an exact match for the given lat/lon
    exact_match = collection.find_one({"location.coordinates": [lon, lat]})
    
    if exact_match:
        return exact_match.get("PlaceId")  # ✅ Return exact match if found

    # 🔹 Step 2: Find the nearest place within `max_distance`
    query_nearby = {
        "location": {
            "$nearSphere": {
                "$geometry": {"type": "Point", "coordinates": [lon, lat]},
                "$maxDistance": max_distance  # Search within 30 meters
            }
        }
    }

    nearby_result = collection.find_one(query_nearby)

    return nearby_result.get("PlaceId") if nearby_result else None  # ✅ Return nearest or None





def format_event(event, favourite_event_ids):
    print("ids :- ",favourite_event_ids)
    """Format event object and check if it's a user favorite."""
    return {
        "EventId": event.get("ActivityId"),
        "CityId": event.get("CityId"),
        "PlaceId": event.get("PlaceId"),
        "PlaceName": event.get("Title"),  # Assuming Title is place name
        "EventTitle": event.get("Title"),
        "EventDescription": event.get("Description"),
        "EventImage": event.get("AttachmentUrl"),
        "EventDate": event.get("ActivityDate"),
        "EventViews": event.get("ViewCount", 0),
        "HashTag": f"{event.get('Hashtag1', '')} {event.get('Hashtag2', '')} {event.get('Hashtag3', '')} {event.get('Hashtag4', '')} {event.get('Hashtag5', '')}".strip(),
        "FavCount": event.get("LikeCount", 0),
        "IsUserFavourite": event.get("ActivityId") in favourite_event_ids,  # Check if in user's favorite list
        # "isUserFavourite": event.get("ActivityId") in favourite_event_ids,  # Check if in user's favorite list
        "TimeLapse": "D"  # Static value, modify logic if required
    }
    
    
    
    
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates the distance (in meters) between two latitude/longitude points using the Haversine formula."""
    R = 6371000  # Radius of Earth in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance_meters = R * c  # Distance in meters
    distance_km = distance_meters / 1000  # Convert to kilometers
    distance_miles = distance_km * 0.621371  # Convert to miles

    return round(distance_km, 2), round(distance_miles, 2)




# def transform_activity(activity):
    
#     user=USER_COLLECTION.find_one({"UserId":activity["CreatedBy"]},{"password":0})
    
    
#     return {
#         "Distance": activity.get("Distance", None),  # Add logic to calculate if needed
#         "Latitude": activity.get("Latitude"),
#         "Longitude": activity.get("Longitude"),
#         "timestamp": activity.get("CreatedDate"),
#         "type": activity.get("ActivityType"),
#         "id": activity.get("ActivityId"),
#         "cityId": activity.get("CityId"),
#         "placeId": activity.get("PlaceId"),
#         "placename": activity.get("Title"),
#         "userId": activity.get("CreatedBy"),
#         "comment_text": activity.get("Description"),
#         "comment_likecount": activity.get("LikeCount"),
#         "comment_dislikecount": activity.get("DisLikeCount"),
#         "inLocation": activity.get("InLocation", False),
#         "favorites": True if activity.get("CreatedBy") in activity.get("LikedUsers") else False,  # Default value, can be fetched from user favorites list
#         "comment_likes": activity.get("IsLiked", False),
#         "comment_dislikes": False,  # Not available in schema, can be inferred if needed
#         "imageUrl": activity.get("AttachmentUrl"),  # Assuming images are in this field
#         "video_thumbnailurl": activity.get("ThumbnailUrl"),
#         "video_videourl": activity.get("AttachmentUrl") if activity.get("ActivityType")=="Video" else None,  # Assuming no direct video field
#         "viewcount": activity.get("ViewCount"),
#         "videos_likecount": None,  # Adjust if video-like count exists
#         "videos_dislikecount": None,  # Adjust if video-dislike count exists
#         "uploader_userinfo": user,
#         "subcomments": None,  # Assuming no subcomments in schema
#         "emojiCount": [
#             {"emojiUrl": "https://scouter-file2.s3.amazonaws.com/Emojis/1F4E8_color.png", "count": 0},
#             {"emojiUrl": "https://scouter-file2.s3.amazonaws.com/Emojis/1F48A_color.png", "count": 0},
#             {"emojiUrl": "https://scouter-file2.s3.amazonaws.com/Emojis/1F351_color.png", "count": 0},
#         ],
#     }


def get_activities(place_id, page=1, page_size=10):
    # Pagination logic
    skip = (page - 1) * page_size
    limit = page_size

    # MongoDB aggregation pipeline for optimized query
    pipeline = [
        {"$match": {"PlaceId": place_id}},
        {"$sort": {"CreatedDate": -1}},  # Sort by latest activity
        {"$skip": skip},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "User",
                "localField": "CreatedBy",
                "foreignField": "UserId",
                "as": "uploader_userinfo",
            }
        },
        {"$unwind": {"path": "$uploader_userinfo", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 0,  # Exclude MongoDB ID
                "Distance": 1,
                "Latitude": 1,
                "Longitude": 1,
                "Timestamp": "$CreatedDate",
                "Type": "$ActivityType",
                "Id": "$ActivityId",
                "CityId": "$CityId",
                "PlaceId": "$PlaceId",
                "Placename": "$Title",
                "UserId": "$CreatedBy",
                "Comment_text": "$Description",
                "Comment_likecount": "$LikeCount",
                "InLocation": {"$ifNull": ["$InLocation", False]},
                "Favorites": {"$in": ["$CreatedBy", "$LikedUsers"]},
                "Comment_likes": {"$ifNull": ["$IsLiked", False]},
                "ImageUrl": "$AttachmentUrl",
                "Video_thumbnailurl": "$ThumbnailUrl",
                "Video_videourl": {
                    "$cond": {"if": {"$eq": ["$ActivityType", "Video"]}, "then": "$AttachmentUrl", "else": None}
                },
                "Viewcount": "$ViewCount",
                "Videos_likecount": None,
                "Videos_dislikecount": None,
                "Uploader_userinfo": {
                    "UserId": "$uploader_userinfo.UserId",
                    "UserName": "$uploader_userinfo.UserName",
                    "ProfilePicture": "$uploader_userinfo.ProfilePicture",
                },
                "Subcomments": None,
                "EmojiCount": [
                    {"EmojiUrl": "https://scouter-file2.s3.amazonaws.com/Emojis/1F4E8_color.png", "count": 0},
                    {"EmojiUrl": "https://scouter-file2.s3.amazonaws.com/Emojis/1F48A_color.png", "count": 0},
                    {"EmojiUrl": "https://scouter-file2.s3.amazonaws.com/Emojis/1F351_color.png", "count": 0},
                ],
            }
        },
    ]
    total_count = ACTIVITY_COLLECTION.count_documents({"PlaceId": place_id})
    activities = list(ACTIVITY_COLLECTION.aggregate(pipeline))
    
    return {
            "success": True,
            "data": activities,
            "page": page,
            "pageSize": page_size,
            "total": total_count
        }














def send_notifications_to_all(title, message,device_tokens, image_url=None, place_id=None):
    """
    Sends push notifications to all active users in batches of 450.
    
    :param title: Notification title
    :param message: Notification message
    :param image_url: Optional image URL for rich notifications
    :param place_id: Optional custom data (e.g., Place ID)
    :return: JSON response with success/failure count and batch results
    """
    try:
        batch_size = 450  # ✅ Batch size set to 450 (below FCM limit of 500)
        total_sent = 0
        total_failed = 0
        batch_results = []

        # ✅ Send notifications in batches of 450
        for i in range(0, len(device_tokens), batch_size):
            batch_tokens = device_tokens[i:i + batch_size]
            
            message_data = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=message,
                    image=image_url if image_url else None
                ),
                tokens=batch_tokens,
                data={"PlaceId": place_id} if place_id else {},
            )
            print("after messaging ")
            response = messaging.send_multicast(message_data)
            total_sent += response.success_count
            total_failed += response.failure_count
            batch_results.append({
                "batch_start": i + 1,
                "batch_end": i + len(batch_tokens),
                "success_count": response.success_count,
                "failure_count": response.failure_count
            })
#         print({
#             "TotalUsers": len(device_tokens),
#             "TotalSent": total_sent,
#             "TotalFailed": total_failed,
#             "Batches": batch_results
#         }
# )
        return {
            "TotalUsers": len(device_tokens),
            "TotalSent": total_sent,
            "TotalFailed": total_failed,
            "Batches": batch_results
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    
    
def send_push_notification_user(title, message,device_token, image_url=None, place_id=None):
    """Send a push notification with custom data (Supports Android & iOS)"""
    print("in messaging part ")
    try:
        message = messaging.Message(
    
            data={  # ✅ Custom Data Payload
                "PlaceId": place_id,
                # "ImageUrl":image_url,
            },
            token=device_token,
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        mutable_content=True,  # ✅ Enables rich notifications (image support in iOS)
                        alert=messaging.ApsAlert(title=title, body=message)
                    )
                ),
                fcm_options=messaging.APNSFCMOptions(
                    image=image_url  # ✅ Image for iOS
                )
            )
        )

        response = messaging.send(message)
        print(response)
        return {
                "TotalUsers": 1,
                "TotalSent": 1,
                "TotalFailed": 0,
                "Batches": ""
            }
    except Exception as error :
        print(error)
        return {"error":error}
