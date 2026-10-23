from flask_jwt_extended import get_jwt_identity
from src.app import User, db
from http import HTTPStatus
from functools import wraps


def requires_role(role_name):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            user_id = int(get_jwt_identity())
            user = db.get_or_404(User, user_id)

            if user.role.name != role_name:
                return {
                    "message": f"{role_name} access required"
                }, HTTPStatus.FORBIDDEN  # 403 Forbidden, pois o usuário está autenticado, mas não tem permissão para acessar essa rota.
            return func(*args, **kwargs)

        return wrapped

    return decorator


def elevado_ao_quadrado(numero):
    return numero**2
