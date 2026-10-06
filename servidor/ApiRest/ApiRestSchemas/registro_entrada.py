from pydantic import BaseModel, EmailStr, Field


class RegistroEntrada(BaseModel):
    email: EmailStr
    nick: str = Field(min_length=1, max_length=30)
    contrasena: str = Field(min_length=8, max_length=64)
