from pydantic import BaseModel, ConfigDict

from servidor.logica.enums import EstadoUsuario, Rol


class UsuarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nick: str
    rol: Rol
    estado: EstadoUsuario
