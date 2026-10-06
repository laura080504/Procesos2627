from pydantic import BaseModel, Field


class NuevaContrasenaEntrada(BaseModel):
    token: str = Field(min_length=1)
    contrasena: str = Field(min_length=8, max_length=64)
