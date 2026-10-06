from dataclasses import dataclass

from servidor.dominio.entities.sesion import Sesion
from servidor.dominio.entities.usuario import Usuario


@dataclass(frozen=True)
class InicioSesionResultado:
    sesion: Sesion
    usuario: Usuario
