import os

import click
from datetime import datetime
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
import jwt
import sqlalchemy as sa  # opcional, apenas para facilitar a leitura do código, pois o SQLAlchemy é muito grande e complexo, e o import sqlalchemy as sa é uma forma de abreviar o nome do módulo, para não precisar escrever sqlalchemy toda vez que for usar alguma função ou classe do SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import flask_migrate
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    JWTManager,
)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
migrate = flask_migrate.Migrate()
jwt = JWTManager()


class Role(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    user: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self) -> str:
        return f"Role(id={self.id!r}, name={self.name!r})"


class User(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(80), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    role_id: Mapped[int] = mapped_column(sa.ForeignKey("role.id"))
    role: Mapped["Role"] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, active={self.active!r})"  # Melhora a visualização do objeto User quando for printado, mostrando o id, o username e o status ativo do usuário.


class Post(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    body: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    created: Mapped[datetime] = mapped_column(sa.DateTime, server_default=sa.func.now())
    author_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("user.id"), nullable=False
    )

    def __repr__(self) -> str:
        return f"Post(id={self.id!r}, title={self.title!r}, author_id={self.author_id!r})"  # Melhora a visualização do objeto Post quando for printado, mostrando o id, o título e o id do autor do post.


@click.command("init-db")  # Cria comandos de terminal para inicializar o banco de dados
def init_db_command():
    """Clear the existing data and create new tables."""
    global db
    with current_app.app_context():
        db.create_all()
    click.echo("Initialized the database.")


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI=os.environ[
            "DATABASE_URL"
        ],  # Conectando o banco de dados SQLite com o Flask, criando o arquivo diobank.sqlite dentro da pasta instance do projeto
        JWT_SECRET_KEY="chave-de-teste-com-mais-de-32-caracteres-123",  # simple authentication for JWT, in a real application you should use a more secure key and store it in an environment variable or a configuration file
    )  # Vai jogar na pasta instance do projeto, que é uma pasta que não é versionada no Git, e que é criada automaticamente pelo Flask quando o projeto é iniciado

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register cli commands
    app.cli.add_command(init_db_command)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register blueprints
    from src.controllers import user
    from src.controllers import post
    from src.controllers import auth
    from src.controllers import role

    app.register_blueprint(user.app)
    app.register_blueprint(post.app)
    app.register_blueprint(auth.app)
    app.register_blueprint(role.app)

    return app
