import pytest

from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioServices.calcular_estado_usuario import calcular_estado_usuario


def prueba_variante6_local_sin_confirmar_queda_pendiente():
    assert calcular_estado_usuario(
        {"proveedor": "local", "confirmado": False, "eliminado": False}
    ) == {"estado": "pendiente", "puedeIniciarSesion": False}


def prueba_variante6_oauth_puede_iniciar_sesion_sin_confirmar():
    assert calcular_estado_usuario(
        {"proveedor": "oauth", "confirmado": False, "eliminado": False}
    ) == {"estado": "activo", "puedeIniciarSesion": True}


def prueba_variante6_eliminado_no_puede_iniciar_sesion():
    assert calcular_estado_usuario(
        {"proveedor": "oauth", "confirmado": True, "eliminado": True}
    ) == {"estado": "eliminado", "puedeIniciarSesion": False}


def prueba_variante6_rechaza_proveedor_desconocido():
    with pytest.raises(EstadoNoValido, match="local u oauth"):
        calcular_estado_usuario({"proveedor": "google", "confirmado": False, "eliminado": False})


def prueba_variante6_rechaza_un_campo_que_no_es_booleano():
    with pytest.raises(EstadoNoValido, match="booleanos"):
        calcular_estado_usuario({"proveedor": "local", "confirmado": "false", "eliminado": False})
