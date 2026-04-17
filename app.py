import json
from typing import Dict

from flask import Flask
from flask import render_template

app = Flask(__name__)


def read_blogs_from_json(json_file_path):
    """ " Loads a JSON file and returns a dictionary of data"""
    with open(json_file_path, encoding="utf-8") as json_file:
        data = json.load(json_file)
        return data


@app.route("/")
def index():
    blog_posts = read_blogs_from_json("blog_posts.json")
    return render_template("index.html", blog_posts=blog_posts)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
