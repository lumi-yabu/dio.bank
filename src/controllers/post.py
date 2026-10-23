from flask import Blueprint, request
from src.app import Post, db
from sqlalchemy import inspect
from http import (
    HTTPStatus,
)

app = Blueprint("post", __name__, url_prefix="/posts")


def _create_post():
    data = request.json
    post = Post(title=data["title"], body=data["body"], author_id=data["author_id"])
    db.session.add(post)
    db.session.commit()


def _list_posts():
    query = db.select(Post)
    results = db.session.execute(query).scalars()
    return [
        {
            "id": post.id,
            "title": post.title,
            "body": post.body,
            "created": post.created.isoformat(),
            "author_id": post.author_id,
        }
        for post in results
    ]


@app.route("/", methods=["GET", "POST"])
def list_or_create_post():
    if request.method == "POST":
        _create_post()
        return {"message": "Post created successfully"}, HTTPStatus.CREATED

    else:
        return {"posts": _list_posts()}


@app.route(
    "/<int:post_id>", methods=["GET"]
)  # quando é GET não precisa colocar o methods=["GET"], pois o GET é o método padrão do HTTP, então não precisa especificar.
def get_post(post_id):
    post = db.get_or_404(Post, post_id)
    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "created": post.created.isoformat(),
        "author_id": post.author_id,
    }


@app.route("/<int:post_id>", methods=["PATCH", "PUT"])
def update_post(post_id):
    post = db.get_or_404(Post, post_id)
    data = request.json
    mapper = inspect(Post)
    for column in mapper.attrs:
        if column.key in data:
            setattr(post, column.key, data[column.key])
    db.session.commit()

    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "created": post.created.isoformat(),
        "author_id": post.author_id,
    }


@app.route("/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    db.session.delete(post)
    db.session.commit()
    return "", HTTPStatus.NO_CONTENT
