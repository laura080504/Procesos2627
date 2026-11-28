from pydantic import BaseModel, EmailStr, Field, field_validator

from Servidor.Dominio.DominioServices.politica_contrasena import validar_contrasena


class RegistroEntrada(BaseModel):
    email: EmailStr
    nick: str = Field(min_length=1, max_length=30)
    contrasena: str = Field(min_length=8, max_length=64)

    @field_validator("email")
    @classmethod
    def email_normalizado(cls, valor: str) -> str:
        return valor.strip().lower()

    @field_validator("nick")
    @classmethod
    def nick_sin_espacios_vacios(cls, valor: str) -> str:
        limpio = valor.strip()
        if not limpio:
            raise ValueError("El usuario no puede estar vacío")
        return limpio

    @field_validator("contrasena")
    @classmethod
    def contrasena_politica(cls, valor: str) -> str:
        return validar_contrasena(valor)
