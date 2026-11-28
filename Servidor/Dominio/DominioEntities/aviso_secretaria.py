from dataclasses import dataclass
from datetime import date
from uuid import uuid4

from Servidor.Dominio.DominioEnums.tipo_aviso_secretaria import TipoAvisoSecretaria


@dataclass(frozen=True)
class AvisoSecretaria:
    """Charla, taller, propuesta u aviso oficial publicado por secretaría."""

    titulo: str
    tipo: TipoAvisoSecretaria
    fecha: date
    hora: str
    lugar: str | None = None
    url: str | None = None
    descripcion: str | None = None
    id: str | None = None

    def con_id(self) -> "AvisoSecretaria":
        if self.id:
            return self
        return AvisoSecretaria(
            titulo=self.titulo,
            tipo=self.tipo,
            fecha=self.fecha,
            hora=self.hora,
            lugar=self.lugar,
            url=self.url,
            descripcion=self.descripcion,
            id=nuevo_id_aviso_secretaria(),
        )


def nuevo_id_aviso_secretaria() -> str:
    return uuid4().hex
