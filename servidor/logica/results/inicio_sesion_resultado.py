from dataclasses import dataclass

from servidor.logica.entities.sesion import Sesion
from servidor.logica.entities.usuario import Usuario


@dataclass(frozen=True)
class InicioSesionResultado:
    sesion: Sesion
    usuario: Usuario
