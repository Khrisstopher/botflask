import pytest

from app.utils.validators import validar_contraseña


@pytest.mark.parametrize(
    "contraseña, esperada",
    [
        ("Ab1", False),
        ("Abcdefg1", True),
        ("abcdefgh1", False),
        ("ABCDEFGH1", False),
        ("Abcdefgh", False),
        ("", False),
    ],
)
def test_validar_contraseña(contraseña, esperada):
    assert validar_contraseña(contraseña) is esperada
