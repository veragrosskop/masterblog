import json
from typing import Dict, List

from flask import Flask, request, redirect
from flask import render_template

app = Flask(__name__)


def read_blogs_from_json(json_file_path) -> List[Dict]:
    """Loads a JSON file and returns a dictionary of data"""
    with open(json_file_path, encoding="utf-8") as json_file:
        data = json.load(json_file)
        return data


def write_blogs_to_json(json_file_path: str, data: List[Dict]) -> None:
    """Writes blog data to a JSON file"""
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def get_next_id(blog_posts) -> int:
    """Returns the next post id (not accounting for gap id's in existing posts)."""
    max_id = max(post["id"] for post in blog_posts)
    return max_id + 1


def add_post(author, title, content, json_file_path):
    """Creates a new blog_post dictionary and adds it to the database"""
    blog_posts = read_blogs_from_json(json_file_path)
    blog_post = {
        "author": author,
        "title": title,
        "content": content,
        "id": get_next_id(blog_posts),
    }
    blog_posts.append(blog_post)
    write_blogs_to_json(json_file_path=json_file_path, data=blog_posts)


def remove_post(post_id, json_file_path):
    """Removes a post from the database"""
    blog_posts = read_blogs_from_json(json_file_path)
    blog_posts = [post for post in blog_posts if post["id"] != post_id]
    write_blogs_to_json(json_file_path=json_file_path, data=blog_posts)


@app.route("/")
def index():
    blog_posts = read_blogs_from_json("blog_posts.json")
    return render_template("index.html", blog_posts=blog_posts)


@app.route("/add", methods=["POST", "GET"])
def add():
    error_msg = ""
    json_file_path = "blog_posts.json"
    if request.method == "POST":
        # Grab data from form
        author = request.form["author"]
        title = request.form["title"]
        content = request.form["content"]

        # validate form data
        if len(author) > 0 and len(title) > 0 and len(content) > 0:
            # continue to homepage if valid
            add_post(author, title, content, "blog_posts.json")
            return redirect("/")
        else:
            # display error message
            error_msg = "Please fill in author, title, and content"
    return render_template("add_form.html", message=error_msg)


@app.route("/delete/<int:post_id>", methods=["POST"])
def delete(post_id):
    remove_post(post_id=post_id, json_file_path="blog_posts.json")
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
