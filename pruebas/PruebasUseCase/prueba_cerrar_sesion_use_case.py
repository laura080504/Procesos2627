from datetime import datetime, timedelta, timezone

from Servidor.Dominio.DominioCommands.cerrar_sesion_command import CerrarSesionCommand
from Servidor.Dominio.DominioEntities.sesion import Sesion
from Servidor.Dominio.DominioUseCases.cerrar_sesion_use_case import CerrarSesionUseCase


def prueba_cerrar_sesion_elimina_la_sesion(repositorio_sesiones):
    sesion = Sesion("token", "laura@ejemplo.com", datetime.now(timezone.utc) + timedelta(hours=1))
    repositorio_sesiones.guardar(sesion)
    CerrarSesionUseCase(repositorio_sesiones).ejecutar(CerrarSesionCommand("token"))
    assert repositorio_sesiones.obtener("token") is None
