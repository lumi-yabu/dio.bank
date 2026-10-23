from flask import Blueprint, request
from src.app import Role, db
from http import (
    HTTPStatus,
)  # código numérico do status code vai ser dado automaticamente com esse módulo

app = Blueprint("role", __name__, url_prefix="/roles")


@app.route("/", methods=["POST"])
def create_role():
    data = request.json
    role = Role(name=data["name"])
    db.session.add(role)
    db.session.commit()
    return {
        "message": "Role created successfully"
    }, HTTPStatus.CREATED  # conforme o padrão REST, precisa ter um status code (201) para informar que a operação de criação foi bem sucedida.
