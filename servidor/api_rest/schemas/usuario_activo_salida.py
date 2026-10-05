from pydantic import BaseModel


class UsuarioActivoSalida(BaseModel):
    email: str
    activo: bool
