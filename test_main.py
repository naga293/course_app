from fastapi.testclient import TestClient
from main import app
 
client=TestClient(app)

def get_courses():
    response = client.get("/courses/")
    courses=response.json()
    assert response.status_code==200
    return courses

def test_list_courses():
    courses=get_courses()
    assert isinstance(courses, list)

def test_list_courses_sort_by_name():
    response = client.get("/courses/?sort_by=name")
    assert response.status_code == 200
    courses = response.json()
    assert courses == sorted(courses, key=lambda x: x['name'])

def test_list_courses_sort_by_date():
    response = client.get("/courses/?sort_by=date")
    assert response.status_code == 200
    courses = response.json()
    assert courses == sorted(courses, key=lambda x: x['date'], reverse=True)

def test_list_courses_sort_by_rating():
    response = client.get("/courses/?sort_by=rating")
    assert response.status_code == 200
    courses = response.json()
    assert courses == sorted(courses, key=lambda x: x.get('rating', 0), reverse=True)

def test_list_courses_with_domain_filter():
    response = client.get("/courses/?domain=programming")
    assert response.status_code == 200
    courses = response.json()
    assert all('programming' in course['domain'] for course in courses)

def test_get_course():
    courses = get_courses()
    course_id=courses[0]["id"]
    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    assert response.json()["name"] == courses[0]["name"]

def test_get_chapter():
    courses = get_courses()
    course_id=courses[0]["id"]
    chapter=courses[0]["chapters"][0]
    chapter_name=chapter["name"]
    response = client.get(f"/courses/{course_id}/chapters/{chapter_name}")
    assert response.status_code == 200
    assert response.json()["name"] == chapter_name
    assert response.json()["text"]==chapter["text"]
    assert response.json()["rating"]==chapter["rating"]

def test_rate_chapter():
    courses = get_courses()
    course_id=courses[0]["id"]
    chapter=courses[0]["chapters"][0]
    chapter_name=chapter["name"]
    chapter_rating=chapter["rating"]

    response = client.post(f"/courses/{course_id}/rate_chapter/{chapter_name}?rating=5")
    assert response.status_code == 422
    
    new_rating=1
    response = client.post(f"/courses/{course_id}/rate_chapter/{chapter_name}?rating={new_rating}")
    if chapter_rating==new_rating:
        assert response.status_code ==400
    else:
        assert response.status_code ==200
        assert response.json()["rating"]==1

    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    assert response.json()["rating"]==1
