from dataclasses import dataclass

from servidor.logica.enums.estado_usuario import EstadoUsuario
from servidor.logica.enums.rol import Rol


@dataclass
class Usuario:
    email: str
    nick: str
    contrasena_hash: str
    rol: Rol = Rol.USUARIO
    estado: EstadoUsuario = EstadoUsuario.ACTIVO
