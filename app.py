import json
from typing import Dict, List, Tuple

from flask import Flask, request, redirect
from flask import render_template

app = Flask(__name__)

JSON_BLOG_FILE_PATH = "blog_posts.json"

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
    if len(blog_posts) == 0:
        return 1
    else:
        max_id = max(post["id"] for post in blog_posts)
    return max_id + 1


def get_post_by_id(blog_posts, post_id):
    for i, post in enumerate(blog_posts):
        if post["id"] == post_id:
            return i, post
    return None, None


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


# --------------------------
#       APP ROUTES
# --------------------------


@app.route("/")
def index():
    blog_posts = read_blogs_from_json(JSON_BLOG_FILE_PATH)
    return render_template("index.html", blog_posts=blog_posts)


@app.route("/add", methods=["POST", "GET"])
def add():
    error_msg = ""
    json_file_path = "blog_posts.json"
    if request.method == "POST":
        is_valid_author = False
        is_valid_title = False
        is_valid_content = False

        # Grab data from form
        author_input = request.form["author"].strip()
        if author_input == "":
            author = "Anonymous"
            is_valid_author = True
        elif not author_input.isalpha():
            error_msg += "Please fill in an author, with alphabetical characters only or leave blank for Anonymous."
        elif len(author_input) > 0:
            author = author_input
            is_valid_author = True

        title_input = request.form["title"].strip()
        if (not title_input.isalpha()) or title_input == "":
            error_msg += " Please fill in a title, with alphabetical characters only."
        elif len(title_input) > 0:
            title = title_input
            is_valid_title = True

        content_input = request.form["content"].strip()
        if content_input == "":
            error_msg += " Please fill in a content."
        elif len(content_input) > 0:
            content = content_input
            is_valid_content = True

        # validate form data
        if is_valid_author and  is_valid_title and is_valid_content:
            # continue to homepage if valid
            add_post(author, title, content, JSON_BLOG_FILE_PATH)
            return redirect("/")
        else:
            # display error message
            if error_msg == "":
                error_msg = "Please fill in a valid author, title, and content"
    return render_template("add_form.html", message=error_msg)


@app.route("/delete/<int:post_id>", methods=["POST", "GET"])
def delete(post_id):
    blog_posts = read_blogs_from_json(JSON_BLOG_FILE_PATH)
    _, post = get_post_by_id(blog_posts, post_id)

    if post is None:
        return "Post not found", 404

    if request.method == "POST":
        remove_post(post_id=post_id, json_file_path=JSON_BLOG_FILE_PATH)
        return redirect("/")

    return render_template("confirm_delete.html", post=post)


@app.route("/update/<int:post_id>", methods=["POST", "GET"])
def update(post_id):
    error_msg = ""
    json_file_path = JSON_BLOG_FILE_PATH
    blog_posts = read_blogs_from_json(json_file_path)
    i, post = get_post_by_id(blog_posts, post_id)
    if post is None or i is None:
        return "Post not found", 404

    if request.method == "POST":
        author = request.form.get("author", "")
        title = request.form.get("title", "")
        content = request.form.get("content", "")
        if not (author == "" or title == "" or content == ""):
            blog_posts[i] = {
                "id": post_id,
                "author": author,
                "title": title,
                "content": content,
            }
            write_blogs_to_json(json_file_path=json_file_path, data=blog_posts)
            return redirect("/")
        else:
            error_msg = "Please fill in author, title, and content"
    return render_template("update_form.html", message=error_msg, post=post)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
