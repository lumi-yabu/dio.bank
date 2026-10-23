## Gerando e configurando acesso ao banco de dados SQLite com o Flask
import sqlite3
from datetime import datetime

import click
from flask import (
    current_app,
    g,
)  # g é uma variável que tem tudo registrado globalmente na aplicação, e o current_app é uma variável que tem tudo registrado no app atual do Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop(
        "db", None
    )  # Procura valores na variável g da chave db, e se não encontrar, retorna None

    if db is not None:
        db.close()


def init_db():  # Esse método executa o script SQL que está no arquivo schema.sql, criando as tabelas do banco de dados
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")  # Cria comandos de terminal para inicializar o banco de dados
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


sqlite3.register_converter(  # Converte os valores do tipo timestamp do banco de dados para o tipo datetime do Python (datetime.datetime)
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)


def init_app(app):
    app.teardown_appcontext(
        close_db
    )  # Quando encerrar o contexto da aplicação, fecha o banco de dados
    app.cli.add_command(
        init_db_command
    )  # Registra o comando init-db no terminal do Flask/app, para que seja possível inicializar o banco de dados com o comando flask init-db
