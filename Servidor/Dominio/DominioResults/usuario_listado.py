from dataclasses import dataclass, field

from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura


@dataclass(frozen=True)
class UsuarioListado:
    usuario: Usuario
    asignaturas: list[str] = field(default_factory=list)
    media: float | None = None
    curso: CursoAsignatura | None = None
