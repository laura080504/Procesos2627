from dataclasses import dataclass

from servidor.logica.enums import EstadoUsuario, Rol


@dataclass
class Usuario:
    nick: str
    rol: Rol = Rol.USUARIO
    estado: EstadoUsuario = EstadoUsuario.ACTIVO
