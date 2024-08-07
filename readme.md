**Description**

- This repo contains a containerized Fast API application with APIs that communicate with MongoDB. They have the below mentioned functionalities
     - `/courses/` - This endpoint lists all courses. This API supports filtering by domain and sorting by name, rating and date.
    - `courses/course_id/` - get a particular course info by passing the course_id
    - `courses/course_id/chapters/chapter_name/` - get a particuloar chapter info by passing course id and chapter name
    - `courses/course_id/rate_Chapter/chapter_name/?rating=rating_value`- rate a chapter as 1 - positive, -1 -negative and 0-neutral. This also updates the rating of the course by aggregating ratings of all chapters.

- It also contains a script which creates collections and indices in mongo. It also populates data given in `course.json` file.

**Steps to Follow:**

- Please run the below command to run the complete setup.

    `docker compose up -d`
- Please run the below command to create collections,indexes and populate data provided in `course.json` file. There is a unique course name constraint so even if you run it multiple times it wont create duplicates
`docker exec -it course_container python population_script.py`
- Please run  the below command to run tests. Tests only pass if you run the populate script before hand. There is no seperate database collection for tests adn we are not creating extra data for the tests.
` docker exec -it course_container python -m pytest`

- You will be able to access swagger from `http://127.0.0.1:10000/docs/` in your browser after running the first command

**Other Improvements which can be done:**

The below enhancements can be done to this applciation. I did not do it now due to time limitations.
- use an independent test DB with setup and tear down instead of using the main application's DB. I generally use Django and this flow is straightforward in that framework. Here I found some solutions to implement the same but they seemed way too hacky and not standard. 
- write a make file with an alias which automatically turns up the docker and run the db population script