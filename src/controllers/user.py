from flask import Blueprint, request
from src.app import User, db
from sqlalchemy import inspect
from flask_jwt_extended import jwt_required
from src.utils import requires_role
from http import (
    HTTPStatus,
)  # código numérico do status code vai ser dado automaticamente com esse módulo

app = Blueprint(
    "user", __name__, url_prefix="/users"
)  # no url_prefix precisa colocar o nome dos recursos no plural (connveção REST)


def _create_user():
    data = request.json
    user = User(
        username=data["username"],
        password=data["password"],
        role_id=data["role_id"],  # se não for passado o role_id, vai ser None
    )

    db.session.add(user)
    db.session.commit()


def _list_users():
    query = db.select(User)
    results = db.session.execute(query).scalars()
    return [
        {
            "id": user.id,
            "username": user.username,
            "role": {
                "id": user.role.id if user.role else None,
                "name": user.role.name if user.role else None,
            },
        }
        for user in results
    ]


@app.route("/", methods=["GET", "POST"])
@jwt_required()  # restringe o acesso a essa rota apenas para usuários autenticados
@requires_role(
    "admin"
)  # restringe o acesso a essa rota apenas para usuários com o papel de "admin"
def list_or_create_user():
    if request.method == "POST":
        _create_user()
        return {
            "message": "User created successfully"
        }, HTTPStatus.CREATED  # conforme o padrão REST, precisa ter um status code (201) para informar que a operação de criação foi bem sucedida.

    else:
        # Lógica para lidar com a requisição GET
        return {"users": _list_users()}


@app.route(
    "/<int:user_id>", methods=["GET"]
)  # quando é GET não precisa colocar o methods=["GET"], pois o GET é o método padrão do HTTP, então não precisa especificar.
def get_user(user_id):
    user = db.get_or_404(User, user_id)
    return {
        "id": user.id,
        "username": user.username,
    }


@app.route(
    "/<int:user_id>", methods=["PATCH"]
)  # PATCH é usado para atualizar parcialmente um recurso, enquanto o PUT é usado para atualizar completamente um recurso. No caso do usuário, como só temos o username, podemos usar o PATCH para atualizar apenas o username.
def update_user(user_id):
    user = db.get_or_404(User, user_id)
    data = request.json
    # Primeira forma intuitiva de UPDATE, mas não é a melhor forma, pois se o modelo User tiver muitos atributos, teremos que escrever um if para cada atributo, o que não é escalável.
    if "username" in data:
        user.username = data["username"]
        db.session.commit()

    # forma mais dinâmica de UPDATE,
    # usando o SQLAlchemy para inspecionar o modelo User e verificar se a chave do dicionário data existe no modelo, e se existir, atualizar o valor do atributo correspondente do objeto user.
    # Isso evita ter que escrever um if para cada atributo do modelo, e permite que o código seja mais genérico e reutilizável para outros modelos.
    mapper = inspect(User)
    for column in mapper.attrs:
        if column.key in data:
            setattr(user, column.key, data[column.key])
    db.session.commit()

    return {
        "id": user.id,
        "username": user.username,
    }


@app.route("/<int:user_id>", methods=["DELETE"])
def remove_user(user_id):
    user = db.get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    return "", HTTPStatus.NO_CONTENT
    # conforme o padrão REST, precisa ter um status code (204) para informar que a operação de deleção foi bem sucedida, e não precisa retornar nenhum conteúdo no corpo da resposta.
