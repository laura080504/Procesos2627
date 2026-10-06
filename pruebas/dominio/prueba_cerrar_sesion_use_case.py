from datetime import datetime, timedelta, timezone

from servidor.dominio.commands.cerrar_sesion_command import CerrarSesionCommand
from servidor.dominio.entities.sesion import Sesion
from servidor.dominio.use_cases.cerrar_sesion_use_case import CerrarSesionUseCase


def prueba_cerrar_sesion_elimina_la_sesion(repositorio_sesiones):
    sesion = Sesion("token", "laura@ejemplo.com", datetime.now(timezone.utc) + timedelta(hours=1))
    repositorio_sesiones.guardar(sesion)
    CerrarSesionUseCase(repositorio_sesiones).ejecutar(CerrarSesionCommand("token"))
    assert repositorio_sesiones.obtener("token") is None
