from dataclasses import dataclass, field

from Servidor.Dominio.DominioEntities.usuario import Usuario


@dataclass(frozen=True)
class UsuarioListado:
    usuario: Usuario
    asignaturas: list[str] = field(default_factory=list)
