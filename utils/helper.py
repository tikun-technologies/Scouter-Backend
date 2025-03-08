from flask import jsonify

def apply_filters(filters, filter_info):
    """Applies dynamic filters to a MongoDB query."""
    mongo_query = {}

    for filter_item in filter_info:
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
