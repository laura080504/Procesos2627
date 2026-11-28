from datetime import date

from pydantic import BaseModel, ConfigDict

from Servidor.Dominio.DominioEnums.tipo_aviso_secretaria import TipoAvisoSecretaria


class AvisoSecretariaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    titulo: str
    tipo: TipoAvisoSecretaria
    fecha: date
    hora: str
    lugar: str | None = None
    url: str | None = None
    descripcion: str | None = None
