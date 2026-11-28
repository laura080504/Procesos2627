from pydantic import BaseModel, EmailStr, Field, field_validator


class InicioSesionEntrada(BaseModel):
    email: EmailStr
    contrasena: str = Field(min_length=1, max_length=64)
    recordar: bool = False

    @field_validator("email")
    @classmethod
    def email_normalizado(cls, valor: str) -> str:
        return valor.strip().lower()
