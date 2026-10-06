from dataclasses import dataclass

from Servidor.Dominio.DominioEntities.sesion import Sesion
from Servidor.Dominio.DominioEntities.usuario import Usuario


@dataclass(frozen=True)
class InicioSesionResultado:
    sesion: Sesion
    usuario: Usuario
