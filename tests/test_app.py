import unittest
import os
from app.text import work_text

os.environ['TESTING'] = 'true'

from app import app, mydb, TimelinePost


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def tearDown(self):
        mydb.drop_tables([TimelinePost])
        mydb.create_tables([TimelinePost])

    def test_home(self):
        response = self.client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "<title>MLH Fellow</title>" in html
        for para in work_text:
            assert para in html

    def test_timeline(self):
        response = self.client.get("api/timeline_post")
        assert response.status_code == 200
        assert response.is_json
        json = response.get_json()
        assert "timeline_posts" in json
        assert len(json["timeline_posts"]) == 0

        # Test the GET and POST requests
        TimelinePost.create(name="Dilnaz", email="dilnaz@example.com", content="Post 1")
        TimelinePost.create(name="Daniel", email="daniel@example.com", content="Post 2")
        response = self.client.get("/api/timeline_post")
        assert response.status_code == 200
        json = response.get_json()
        assert len(json["timeline_posts"]) == TimelinePost.select().count()
        posts_in_response = json["timeline_posts"]
        posts_in_database = list(TimelinePost.select().order_by(TimelinePost.created_at.desc()))

        for i in range(len(posts_in_response)):
            assert "name" in posts_in_response[i]
            assert "email" in posts_in_response[i]
            assert "content" in posts_in_response[i]
            assert posts_in_response[i]["name"] == posts_in_database[i].name
            assert posts_in_response[i]["email"] == posts_in_database[i].email
            assert posts_in_response[i]["content"] == posts_in_database[i].content

        # Test the /timeline page

        response = self.client.get("/timeline")
        assert response.status_code == 200
        assert b"<form action=\"/timeline\" method=\"post\">" in response.data
        assert b"Name:" in response.data
        assert b"Email:" in response.data
        assert b"Content:" in response.data
        assert b"Submit" in response.data
        assert b"Name: Dilnaz" in response.data
        assert b"Email: dilnaz@example.com" in response.data
        assert b"Content: Post 1" in response.data
        assert b"Name: Daniel" in response.data
        assert b"Email: daniel@example.com" in response.data
        assert b"Content: Post 2" in response.data

        assert b"Name: Joseph" not in response.data

    def test_malformed_timeline_post(self):
        # POST request missing name
        response = self.client.post("/api/timeline_post",
                                    data={"email": "john@example.com", "content": "Hello world, I'm John!"})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid name" in html

        # POST request with empty content
        response = self.client.post("/api/timeline_post",
                                    data={"name": "John Doe", "email": "john@example.com", "content": ""})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid content" in html

        # POST request with malformed email
        response = self.client.post("/api/timeline_post",
                                    data={"name": "John Doe", "email": "not-an-email",
                                          "content": "Hello world, I'm John!"})
        # print(response.status_code)
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid email" in html
