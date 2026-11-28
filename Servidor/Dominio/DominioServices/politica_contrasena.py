"""Política de contraseñas alineada con NIST (longitud + denylist básica)."""

CONTRASENAS_COMUNES = frozenset(
    {
        "password",
        "password1",
        "password123",
        "12345678",
        "123456789",
        "1234567890",
        "qwerty123",
        "qwertyuiop",
        "abcdefghi",
        "abcdefgh",
        "iloveyou",
        "admin123",
        "welcome1",
        "letmein1",
        "monkey123",
        "dragon123",
        "master123",
        "login123",
        "contraseña",
        "contrasena",
        "contraseña1",
        "universidad",
        "uclm2026",
        "procesos",
        "procesos2627",
    }
)


def validar_contrasena(contrasena: str) -> str:
    if contrasena is None:
        raise ValueError("La contraseña es obligatoria")
    # NIST: no recortar espacios internos; sí rechazar solo whitespace.
    if not contrasena or contrasena.isspace():
        raise ValueError("La contraseña no puede estar vacía")
    if len(contrasena) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if len(contrasena) > 64:
        raise ValueError("La contraseña no puede superar 64 caracteres")
    if contrasena.lower().strip() in CONTRASENAS_COMUNES:
        raise ValueError("Elige una contraseña menos habitual")
    return contrasena
