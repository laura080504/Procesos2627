from pydantic import BaseModel, ConfigDict

from servidor.dominio.enums.estado_usuario import EstadoUsuario
from servidor.dominio.enums.rol import Rol


class UsuarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str
    nick: str
    rol: Rol
    estado: EstadoUsuario
