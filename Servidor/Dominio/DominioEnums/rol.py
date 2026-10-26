from enum import StrEnum


class Rol(StrEnum):
    USUARIO = "usuario"
    PROFESOR = "profesor"
    SUPERADMINISTRADOR = "superadministrador"


def rol_desde_almacen(valor: str) -> Rol:
    if valor == "administrador":
        return Rol.PROFESOR
    return Rol(valor)
