# import uuid
# from faker import Faker
# from pymongo import MongoClient
# import random
# from datetime import datetime

# # Initialize Faker
# fake = Faker()

# # Connect to MongoDB
# from config.db_config import PLACE_COLLECTION
# # Categories of places
# CATEGORIES = ["Restaurant", "Park", "Museum", "Hotel"]

# def generate_random_place():
#     """Generates a random place document."""
#     _id=str(uuid.uuid4())
#     return {
#         "_id":_id,
#         "PlaceId":_id,
#         "name": fake.company(),
#         "address": fake.address(),
#         "city": fake.city(),
#         "latitude": round(random.uniform(-90, 90), 6),
#         "longitude": round(random.uniform(-180, 180), 6),
#         "category": random.choice(CATEGORIES),
#         "rating": round(random.uniform(1, 5), 1),
#         "created_at": datetime.utcnow()
#     }

# # Generate 100 random places
# random_places = [generate_random_place() for _ in range(10000)]

# # Insert into MongoDB
# inserted = PLACE_COLLECTION.insert_many(random_places)

# print(f"Inserted {len(inserted.inserted_ids)} places into MongoDB.")




import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from config.db_config import ACTIVITY_COLLECTION

def generate_random_event(event_id, days_offset):
    """Generate a random test event with a given day offset."""
    now = datetime.utcnow()
    activity_date = now + timedelta(days=days_offset, hours=random.randint(10, 22))
    migrated_date = now - timedelta(days=random.randint(1, 5))  # Migrated within last 5 days
    
    return {
        "_id":f"EVENT_{event_id}",
        "ActivityId": f"EVENT_{event_id}",
        "CityId": f"CITY_{random.randint(1, 5)}",
        "PlaceId": f"PLACE_{random.randint(1, 5)}",
        "Title": random.choice([
            "Live Jazz Night", "Tech Meetup", "Food Festival", "Music Concert", 
            "Art Exhibition", "Comedy Show", "Startup Pitch", "Wine Tasting", 
            "Yoga Retreat", "Science Fair"
        ]),
        "Description": "Join us for an amazing experience at this exclusive event!",
        "AttachmentUrl": f"https://example.com/event_{event_id}.jpg",
        "ActivityDate": activity_date.strftime("%Y-%m-%dT%H:%M:%S"),
        "MigratedDate": migrated_date.strftime("%Y-%m-%dT%H:%M:%S"),
        "ActivityType": "event",
        "ViewCount": random.randint(50, 1000),
        "Hashtag1": random.choice(["#Fun", "#Music", "#Tech", "#Art", "#Food"]),
        "Hashtag2": random.choice(["#Festival", "#Live", "#Event", "#Show"]),
        "LikeCount": random.randint(10, 500)
    }

def insert_test_events():
    """Generate and insert 20 test events into MongoDB."""
    events = []

    for i in range(1, 21):
        if i <= 7:  # First 7 events for tonight
            days_offset = 0
        elif i <= 14:  # Next 7 events for this week
            days_offset = random.randint(1, 6)
        else:  # Remaining 6 events for upcoming
            days_offset = random.randint(7, 30)

        event = generate_random_event(i, days_offset)
        events.append(event)

    ACTIVITY_COLLECTION.insert_many(events)
    print("20 test events inserted successfully!")

# Run the function
insert_test_events()
