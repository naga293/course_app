from typing import List, Optional
import os
import json
from enum import Enum

from bson.objectid import ObjectId
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo import DESCENDING

from utils import get_chapter_from_course


app = FastAPI()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/course_database")
client = MongoClient(MONGO_URI)
db = client.get_database()
# Connect to MongoDB
# db =get_database()
collection = db['courses']

class RatingEnum(str,Enum):
    POSITIVE = 1
    NEUTRAL = 0
    NEGATIVE = -1


class Chapter(BaseModel):
    name: str
    text: str
    rating: Optional[int] = 0  # Rating can be positive, negative, or zero

class Course(BaseModel):
    id: str
    name: str
    date: str
    description: str
    domain: List[str]
    chapters: List[Chapter]
    rating: Optional[int] = 0  # Aggregated rating for the course

@app.get("/courses/", response_model=List[Course])
async def list_courses(
    sort_by: Optional[str] = 'name',
    domain: Optional[str] = None
):
    """
    Get a list of all available courses.

    Query Parameters:
    - sort_by: The field to sort by. Can be 'title' (alphabetical, ascending), 'date' (date added, descending), or 'rating' (total rating, descending).
    - domain: Optional filter to get courses within a specific domain.
    """

    sort_options = {
        'name': [('name', 1)],
        'date': [('date', DESCENDING)],
        'rating': [('rating', DESCENDING)]
    }
    sort_order = sort_options.get(sort_by, [('name', 1)])

    query = {}
    if domain:
        query['domain'] =domain
    courses = list(collection.find(query).sort(sort_order))
    courses=json.loads(json.dumps(courses, default=str))
    courses = [Course(
        id=str(course.get('_id')),
        name=course.get('name'),
        date=str(course.get('date')),
        description=course.get('description'),
        domain=course.get('domain'),
        chapters=course.get('chapters'),
        rating=course.get('rating')
    ) for course in courses]
    return courses

@app.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: str):
    """
    Get the overview of a specific course.

    Parameters:
    - course_id: ID of the course to retrieve.
    """
    course = collection.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course = Course(
        id=str(course.get('_id')),
        name=course.get('name'),
        date=str(course.get('date')),
        description=course.get('description'),
        domain=course.get('domain'),
        chapters=course.get('chapters'),
        rating=course.get('rating')
    )
    return course

@app.get("/courses/{course_id}/chapters/{chapter_name}")
async def get_chapter(course_id: str, chapter_name: str):
    """
    Get specific chapter information.

    Parameters:
    - course_id: ID of the course that contains the chapter.
    - chapter_name: name of the chapter to retrieve.

    """
    course = collection.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    chapter=get_chapter_from_course(course,chapter_name)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    return chapter

@app.post("/courses/{course_id}/rate_chapter/{chapter_name}")
async def rate_chapter(course_id: str, chapter_name: str, rating: RatingEnum):
    """
        Allow users to rate a chapter.

        Parameters:
        - course_id: ID of the course that contains the chapter.
        - chapter_name: name of the chapter to rate.
    """
    course = collection.find_one({"_id":  ObjectId(course_id)})
    rating=int(rating.value)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    chapter=get_chapter_from_course(course,chapter_name)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")


    # Update course total rating
    total_rating = sum(ch.get('rating', 0) for ch in course['chapters'])
    # Update the chapter's rating within the specified course
    result = collection.update_one(
        {"_id": ObjectId(course_id), "chapters.name": chapter_name},
        {"$set": {"chapters.$.rating": rating}}
    )
    
    # Check if the update was successful
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Rating update Failed")

    updated_total_rating=total_rating+rating-chapter.get('rating')
    result = collection.update_one(
    {"_id": ObjectId(course_id)},
    {"$set": {"rating": updated_total_rating}}
    )
    course = collection.find_one({"_id":  ObjectId(course_id)})
    chapter=get_chapter_from_course(course,chapter_name)
    return chapter
