from src.utils import elevado_ao_quadrado, requires_role
import pytest
from http import HTTPStatus


@pytest.mark.parametrize("test_input,expected", [(2, 4), (10, 100), (3, 9)])
def test_eleva_ao_quadrado_sucesso(test_input, expected):
    resultado = elevado_ao_quadrado(test_input)
    assert resultado == expected


@pytest.mark.parametrize(
    "test_input,exc_class,msg",
    [
        (
            "a",
            TypeError,
            "unsupported operand type(s) for ** or pow(): 'str' and 'int'",
        ),
        (
            None,
            TypeError,
            "unsupported operand type(s) for ** or pow(): 'NoneType' and 'int'",
        ),
    ],
)
def test_eleva_ao_quadrado_falha(test_input, exc_class, msg):
    with pytest.raises(
        exc_class
    ) as exc:  # raises do pytest permite especificar o tipo de erro a ser mmostrado
        elevado_ao_quadrado(test_input)
    assert str(exc.value) == msg


def test_requires_role_success(mocker):
    # Given session (parte que forneço dados)
    mock_user = mocker.Mock()
    mock_user.role.name = "admin"

    mocker.patch("src.utils.get_jwt_identity")
    mocker.patch("src.utils.db.get_or_404", return_value=mock_user)
    decorated_function = requires_role("admin")(
        lambda: "success"
    )  # lambda é uma função qualquer que tem como objetivo apenas dar um retorno válido, nesse caso retorna "success"
    # Essa linha permite identificar se a função requires_role foi chamada corretamente

    # When session (parte que executa a função em teste)
    result = decorated_function()

    # Then session (parte que faz a comparação dos retornos/verificação)
    assert result == "success"


def test_requires_role_fail(mocker):
    # Given
    mock_user = mocker.Mock()
    mock_user.role.name = "normal"

    mocker.patch("src.utils.get_jwt_identity")
    mocker.patch("src.utils.db.get_or_404", return_value=mock_user)

    decorated_function = requires_role("admin")(
        lambda: "success"
    )  # lambda é uma função qualquer que tem como objetivo apenas dar um retorno válido, nesse caso retorna "success"
    # Essa linha permite identificar se a função requires_role foi chamada corretamente

    # When
    result = decorated_function()

    # Then
    assert result == (
        {"message": "admin access required"},
        HTTPStatus.FORBIDDEN,
    )  # Atenção: Isso não é uma Exception, e sim, uma tupla contendo um dicionário e um status
