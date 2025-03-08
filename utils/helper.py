from flask import jsonify

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
