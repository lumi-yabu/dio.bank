import pytest
from src.app import Post, db
from sqlalchemy import func
from http import HTTPStatus
from datetime import datetime


def test_get_post_success(client):
    # Given

    post = Post(title="Testing", body="Hello, wolrd", author_id=post.author_id)
    db.session.add(post)
    db.session.commit()

    # When
    response = client.get(f"/post/{post.id}")

    # Then
    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "created": post.created.isoformat(),
        "author_id": post.author_id,
    }


def test_get_post_not_found(client):
    # Given
    post_id = 1

    # When
    response = client.get(f"/users/{post_id}")

    # Then
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_post(client):
    # Given
    payload = {
        "title": "Testing",
        "body": "Hello, world",
        "author_id": 1,
    }

    # When
    response = client.post("/post/", json=payload)

    # Then
    assert response.status_code == HTTPStatus.CREATED
    assert response.json == {"message": "Post created successfully"}
    assert db.session.execute(db.select(func.count(Post.id))).scalar() == 1


@pytest.fixture
def post(app, db):
    """Cria um post no banco de teste."""
    with app.app_context():
        novo = Post(
            title="Meu primeiro post",
            body="Conteúdo do post",
            author_id=1,
            created=datetime(2026, 10, 23, 14, 30, 0),
        )
        db.session.add(novo)
        db.session.commit()
        db.session.refresh(novo)
        yield novo


def test_list_post(client, post):
    # Given - fornecido pela fixture post()
    # When
    response = client.get("/post/")

    # Then
    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        "posts": [
            {
                "id": post.id,
                "title": post.title,
                "body": post.body,
                "created": post.created.isoformat(),
                "author_id": post.author_id,
            }
        ]
    }


def test_list_post_retorna_varios_posts(client, app, db):
    # Given
    with app.app_context():
        db.session.add_all(
            [
                Post(title="A", body="a", author_id=1, created=datetime(2026, 1, 1)),
                Post(title="B", body="b", author_id=2, created=datetime(2026, 1, 2)),
            ]
        )
        db.session.commit()

    # When
    response = client.get("/post/")

    # Then
    assert response.status_code == HTTPStatus.OK
    titulos = [p["title"] for p in response.json["posts"]]
    assert sorted(titulos) == ["A", "B"]


def test_list_post_retorna_json(client):
    response = client.get("/post/")

    assert response.content_type == "application/json"


def test_list_post_nao_aceita_metodo_post(client):
    response = client.post("/post/", json={})

    # ajuste conforme a sua rota: pode ser 405 (não permitido) ou 201 (se a rota também cria)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
