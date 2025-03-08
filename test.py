import uuid
from faker import Faker
from pymongo import MongoClient
import random
from datetime import datetime

# Initialize Faker
fake = Faker()

# Connect to MongoDB
from config.df_config import PLACE_COLLECTION
# Categories of places
CATEGORIES = ["Restaurant", "Park", "Museum", "Hotel"]

def generate_random_place():
    """Generates a random place document."""
    _id=str(uuid.uuid4())
    return {
        "_id":_id,
        "PlaceId":_id,
        "name": fake.company(),
        "address": fake.address(),
        "city": fake.city(),
        "latitude": round(random.uniform(-90, 90), 6),
        "longitude": round(random.uniform(-180, 180), 6),
        "category": random.choice(CATEGORIES),
        "rating": round(random.uniform(1, 5), 1),
        "created_at": datetime.utcnow()
    }

# Generate 100 random places
random_places = [generate_random_place() for _ in range(100)]

# Insert into MongoDB
inserted = PLACE_COLLECTION.insert_many(random_places)

print(f"Inserted {len(inserted.inserted_ids)} places into MongoDB.")
