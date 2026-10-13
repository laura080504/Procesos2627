from pydantic import BaseModel, EmailStr, Field, field_validator


class EditarDatosEntrada(BaseModel):
    email: EmailStr
    nick: str = Field(min_length=1, max_length=30)
    contrasena: str | None = Field(default=None, max_length=64)

    @field_validator("nick")
    @classmethod
    def nick_sin_espacios_vacios(cls, valor: str) -> str:
        limpio = valor.strip()
        if not limpio:
            raise ValueError("El usuario no puede estar vacío")
        return limpio

    @field_validator("contrasena")
    @classmethod
    def contrasena_opcional(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        limpio = valor.strip()
        if not limpio:
            return None
        if not 8 <= len(limpio) <= 64:
            raise ValueError("La contraseña debe tener entre 8 y 64 caracteres")
        return limpio
