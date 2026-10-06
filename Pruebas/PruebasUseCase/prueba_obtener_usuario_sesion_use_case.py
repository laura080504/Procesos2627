from datetime import datetime, timedelta, timezone

import pytest

from Servidor.Dominio.DominioEntities.sesion import Sesion
from Servidor.Dominio.DominioExceptions.sesion_no_valida import SesionNoValida
from Servidor.Dominio.DominioQueries.obtener_usuario_sesion_query import ObtenerUsuarioSesionQuery
from Servidor.Dominio.DominioUseCases.obtener_usuario_sesion_use_case import ObtenerUsuarioSesionUseCase


@pytest.fixture
def use_case(repositorio_sesiones, repositorio_usuarios):
    return ObtenerUsuarioSesionUseCase(repositorio_sesiones, repositorio_usuarios)


def crear_sesion(email: str, horas: int) -> Sesion:
    return Sesion("token", email, datetime.now(timezone.utc) + timedelta(hours=horas))


def prueba_sesion_valida_devuelve_el_usuario(use_case, repositorio_sesiones, usuario_registrado):
    repositorio_sesiones.guardar(crear_sesion(usuario_registrado.email, 1))
    assert use_case.ejecutar(ObtenerUsuarioSesionQuery("token")) == usuario_registrado


def prueba_token_desconocido_lanza_error(use_case):
    with pytest.raises(SesionNoValida):
        use_case.ejecutar(ObtenerUsuarioSesionQuery("inventado"))


def prueba_sesion_caducada_lanza_error_y_se_elimina(use_case, repositorio_sesiones, usuario_registrado):
    repositorio_sesiones.guardar(crear_sesion(usuario_registrado.email, -1))
    with pytest.raises(SesionNoValida):
        use_case.ejecutar(ObtenerUsuarioSesionQuery("token"))
    assert repositorio_sesiones.obtener("token") is None


def prueba_sesion_de_usuario_eliminado_lanza_error(use_case, repositorio_sesiones):
    repositorio_sesiones.guardar(crear_sesion("borrado@ejemplo.com", 1))
    with pytest.raises(SesionNoValida):
        use_case.ejecutar(ObtenerUsuarioSesionQuery("token"))
