from pydantic import BaseModel


class UsuarioActivoSalida(BaseModel):
    nick: str
    activo: bool
