from enum import StrEnum


class Rol(StrEnum):
    USUARIO = "usuario"
    PROFESOR = "profesor"
    SUPERADMINISTRADOR = "superadministrador"


ROLES_GESTION = (Rol.PROFESOR, Rol.SUPERADMINISTRADOR)


def rol_desde_almacen(valor: str) -> Rol:
    if valor == "administrador":
        return Rol.PROFESOR
    # Secretaría es el superadministrador de la escuela (cuenta de arranque).
    if valor == "secretaria":
        return Rol.SUPERADMINISTRADOR
    return Rol(valor)
