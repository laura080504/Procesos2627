from pydantic import BaseModel, EmailStr, Field


class InicioSesionEntrada(BaseModel):
    email: EmailStr
    contrasena: str = Field(min_length=1, max_length=64)
