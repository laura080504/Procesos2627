from dataclasses import dataclass
from datetime import date

from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioEnums.tipo_aviso_secretaria import TipoAvisoSecretaria


@dataclass(frozen=True)
class CrearAvisoSecretariaCommand:
    titulo: str
    tipo: TipoAvisoSecretaria
    fecha: date
    hora: str
    lugar: str | None
    url: str | None
    descripcion: str | None
    solicitante_rol: Rol
