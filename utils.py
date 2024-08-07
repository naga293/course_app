def get_chapter_from_course(course,chapter_name):
    chapter = next((ch for ch in course['chapters'] if ch['name'] == chapter_name), None)
    return chapter
    