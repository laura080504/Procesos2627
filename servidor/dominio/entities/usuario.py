from dataclasses import dataclass

from servidor.dominio.enums.estado_usuario import EstadoUsuario
from servidor.dominio.enums.rol import Rol


@dataclass
class Usuario:
    email: str
    nick: str
    contrasena_hash: str
    rol: Rol = Rol.USUARIO
    estado: EstadoUsuario = EstadoUsuario.ACTIVO
