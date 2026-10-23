# tests/integration/conftest.py
import pytest
from src.app import create_app, db, User, Role


@pytest.fixture()  # é possível passar escopo da fixture, mas pode ser o motivo de failed em tests (tome cuidado)
def app(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.sqlite3'}",
            "JWT_SECRET_KEY": "chave-de-teste-com-mais-de-32-caracteres-123",
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def app_config(app_config):  # recebe a do nível acima
    app_config["JWT_SECRET_KEY"] = "segredo-de-teste"
    return app_config


@pytest.fixture()
def client(
    app,
):  # Tem como finalidade criar uma instância de teste do cliente Flask para enviar requisições
    return app.test_client()


@pytest.fixture
def access_token(client):
    role = Role(name="admin")
    db.session.add(role)
    db.session.commit()

    user = User(username="jane-doe", password="test", role_id=role.id)
    db.session.add(user)
    db.session.commit()

    response = client.post(
        "/auth/login", json={"username": user.username, "password": user.password}
    )
    return response.json["access_token"]
