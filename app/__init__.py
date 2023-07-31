import os
import re
import datetime
from flask import Flask, render_template, request, jsonify
from playhouse.shortcuts import model_to_dict
from dotenv import load_dotenv

# from dotenv import load_dotenv
from app.text import (
    about_text,
    work_text_joseph,
    work_text_dilnaz,
    about_text_dilnaz,
    work_text,
    about_text_maya,
    work_text_maya,
    education_text,
    education_text_dilnaz,
    education_text_joseph,
    education_text_maya,
)
from peewee import *

load_dotenv()

app = Flask(__name__)

if os.getenv("TESTING") == "true":
    print("Running in test mode")
    mydb = SqliteDatabase("file:memory?mode=memory&cache=shared", uri=True)
else:
    mydb = MySQLDatabase(
        os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        port=3306,
    )


class TimelinePost(Model):
    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = mydb


mydb.connect()
mydb.create_tables([TimelinePost])


def mapping(coords):
    markers = ""

    for id, (lat, lon) in enumerate(coords):
        # Create the marker and its pop-up for each shop
        idd = f"a{id}"
        markers += "var {idd} = L.marker([{latitude}, {longitude}]);\
                            {idd}.addTo(map);".format(
            idd=idd,
            latitude=lat,
            longitude=lon,
        )
    return coords, markers


@app.route("/")
def index():
    coords = [
        (34.037945, -117.677852),
        (45.231382, 16.577320),
        (45.537137, 119.137498),
        (48.0196, 66.9237),
        (61.5240, 105.3188),
        (41.3775, 64.5853),
        (38.9637, 35.2433),
        (37.0902, -95.7129),
    ]
    # Render the page with the map
    return render_template(
        "index.html",
        markers=mapping(coords)[1],
        lat=(mapping(coords))[0][0][0],
        lon=(mapping(coords))[0][0][1],
        title="MLH Fellow",
        url=os.getenv("URL"),
        photo="logo",
        about_text=about_text,
        work_text=work_text,
        education_text=education_text,
    )


@app.route("/joseph")
def joseph():
    coords = [(34.037945, -117.677852), (45.231382, 16.577320), (45.537137, 119.137498)]

    # Render the page with the map
    return render_template(
        "index.html",
        markers=mapping(coords)[1],
        lat=(mapping(coords))[0][0][0],
        lon=(mapping(coords))[0][0][1],
        title="Joseph",
        url=os.getenv("URL"),
        photo="logo",
        about_text=about_text,
        work_text=work_text_joseph,
        education_text=education_text_joseph,
    )


@app.route("/maya")
def maya():
    coords = [
        (19.43260, -99.133209),
        (39.9526, -75.1652),
        (6.3690, 34.8888),
        (52.3676, 4.9041),
    ]

    # Render the page with the map
    return render_template(
        "index.html",
        markers=mapping(coords)[1],
        lat=(mapping(coords))[0][0][0],
        lon=(mapping(coords))[0][0][1],
        title="Maya Lekhi",
        url=os.getenv("URL"),
        photo="profile",
        about_text=about_text_maya,
        work_text=work_text_maya,
        education_text=education_text_maya,
    )


@app.route("/dilnaz")
def dilnaz():
    coords = [
        (48.0196, 66.9237),
        (61.5240, 105.3188),
        (41.3775, 64.5853),
        (38.9637, 35.2433),
        (37.0902, -95.7129),
    ]

    # Render the page with the map
    return render_template(
        "index.html",
        markers=mapping(coords)[1],
        lat=(mapping(coords))[0][0][0],
        lon=(mapping(coords))[0][0][1],
        title="Dilnaz Uasheva",
        url=os.getenv("URL"),
        photo="dilnaz",
        about_text=about_text_dilnaz,
        work_text=work_text_dilnaz,
        education_text=education_text_dilnaz,
    )


@app.route("/hobbies")
def hobbies():
    title = "Our Team's Hobbies"
    hobbies_list = [
        {"title": "Reading", "image": "static/img/reading.jpg"},
        {"title": "Gardening", "image": "static/img/gardening.jpg"},
        {"title": "Painting", "image": "static/img/painting.jpg"},
        {"title": "Cooking", "image": "static/img/cooking.jpg"},
    ]

    return render_template("hobbies.html", title=title, hobbies_list=hobbies_list)


@app.route("/api/timeline_post", methods=["POST"])
def post_time_line_post():
    try:
        name = request.form["name"]
    except:
        return jsonify({"error": "Invalid name"}), 400

    try:
        email = request.form["email"]
    except:
        return jsonify({"error": "Invalid email"}), 400

    try:
        content = request.form["content"]
    except:
        return jsonify({"error": "Invalid content"}), 400

    email_pattern = r"[^@]+@[^@]+\.[^@]+"
    if not re.match(email_pattern, email):
        return jsonify({"error": "Invalid email"}), 400
    if content == "":
        return jsonify({"error": "Invalid content"}), 400
    timeline_post = TimelinePost.create(name=name, email=email, content=content)

    return model_to_dict(timeline_post)


@app.route("/api/timeline_post", methods=["GET"])
def get_time_line_post():
    return {
        "timeline_posts": [
            model_to_dict(p)
            for p in TimelinePost.select().order_by(TimelinePost.created_at.desc())
        ]
    }


@app.route("/timeline", methods=["GET", "POST"])
def timeline():
    if request.method == "POST":
        response = post_time_line_post()
        if response[1] == 400:
            return render_template("timeline.html", title="Timeline",
                                   sorted_posts=get_time_line_post()["timeline_posts"], error=response[0]["error"])
    model_dict = get_time_line_post()
    sorted_posts = model_dict["timeline_posts"]
    sorted_posts.sort(key=lambda post: post["created_at"], reverse=True)

    return render_template("timeline.html", title="Timeline", sorted_posts=sorted_posts)


if os.getenv("TESTING") == "true":
    print("Running in test mode")
    mydb = SqliteDatabase('file:memory?mode=memory&cache=shared', url=True)
else:
    mydb = MySQLDatabase(os.getenv("MYSQL_DATABASE"),
                         user=os.getenv("MYSQL_USER"),
                         password=os.getenv("MYSQL_PASSWORD"),
                         host=os.getenv("MYSQL_HOST"),
                         port=3306

                         )

if __name__ == "__main__":
    app.run(debug=True)
