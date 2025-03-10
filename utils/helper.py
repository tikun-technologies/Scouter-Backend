from concurrent.futures import ThreadPoolExecutor
import uuid
from flask import jsonify
from flask_jwt_extended import  jwt_required
from functools import wraps
from flask_jwt_extended import JWTManager
from azure.storage.blob import BlobServiceClient
import requests

jwt = JWTManager() 
def apply_filters(filters, filter_data):
    """Applies dynamic filters to a MongoDB query."""
    mongo_query = {}

    if filter_data.get("filterInfo"):
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