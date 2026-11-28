from pydantic import BaseModel, Field, field_validator

from Servidor.Dominio.DominioServices.politica_contrasena import validar_contrasena


class NuevaContrasenaEntrada(BaseModel):
    token: str = Field(min_length=1)
    contrasena: str = Field(min_length=8, max_length=64)

    @field_validator("contrasena")
    @classmethod
    def contrasena_politica(cls, valor: str) -> str:
        return validar_contrasena(valor)
