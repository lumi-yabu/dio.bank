import pytest
from src.app import app, db


@pytest.fixture
def client(tmp_path):
    # 1. Aponta o app para um arquivo de banco exclusivo deste teste
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_path / 'test.sqlite3'}",
    )

    # 2. Abre o contexto da aplicação
    with app.app_context():
        # 3. Cria as tabelas no banco novo
        db.create_all()

        # 4. Entrega o client ao teste (o teste roda aqui)
        yield app.test_client()

        # 5. Limpeza depois do teste
        db.session.remove()
        db.drop_all()


# tests/conftest.py
@pytest.fixture
def app_config(tmp_path):
    return {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.sqlite3'}",
    }
