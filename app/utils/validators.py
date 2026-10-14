def validar_contraseña(contraseña):
    """Comprueba que la contraseña cumpla los requisitos mínimos."""
    if not contraseña or len(contraseña) < 8:
        return False

    if not any(caracter.isupper() for caracter in contraseña):
        return False

    if not any(caracter.islower() for caracter in contraseña):
        return False

    if not any(caracter.isdigit() for caracter in contraseña):
        return False

    return True
