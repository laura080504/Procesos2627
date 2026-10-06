from dataclasses import dataclass

from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol


@dataclass
class Usuario:
    email: str
    nick: str
    contrasena_hash: str
    rol: Rol = Rol.USUARIO
    estado: EstadoUsuario = EstadoUsuario.ACTIVO
