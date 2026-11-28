from datetime import date

from pydantic import BaseModel, Field

from Servidor.Dominio.DominioEnums.tipo_aviso_secretaria import TipoAvisoSecretaria


class AvisoSecretariaEntrada(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    tipo: TipoAvisoSecretaria
    fecha: date
    hora: str = Field(min_length=4, max_length=5)
    lugar: str | None = Field(default=None, max_length=120)
    url: str | None = Field(default=None, max_length=400)
    descripcion: str | None = Field(default=None, max_length=500)
