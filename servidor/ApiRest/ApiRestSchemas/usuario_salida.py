from pydantic import BaseModel, ConfigDict

from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol


class UsuarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str
    nick: str
    rol: Rol
    estado: EstadoUsuario
