import json
import os
from pymongo import MongoClient, ASCENDING
from datetime import datetime


# Load the JSON data
with open('courses.json') as f:
    courses_data = json.load(f)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/course_database")
client = MongoClient(MONGO_URI)

# Create (or switch to) a database
db = client['course_database']

# Create (or switch to) a collection
collection = db['courses']

# Create indices for efficient retrieval
collection.create_index([('name', ASCENDING)], unique=True)
collection.create_index([('date', ASCENDING)])
collection.create_index([('domain', ASCENDING)])
collection.create_index([('chapters.name', ASCENDING)])

# Convert Unix timestamp to datetime object and insert data
for course in courses_data:
    course['date'] = datetime.utcfromtimestamp(course['date'])
    # Add default rating of 0 to each chapter
    course['rating']=0
    for chapter in course['chapters']:
        chapter['rating'] = 0  # Default rating
    try:
        collection.insert_one(course)
    except Exception as e:
        print(f"Error inserting course {course['name']}: {e}")


print("Courses added and indices created successfully.")

