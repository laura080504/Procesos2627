from datetime import timedelta

import pytest

from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioServices.token_seguro import hash_token
from Servidor.Dominio.DominioUseCases.confirmar_asignacion_rol_use_case import ConfirmarAsignacionRolUseCase
from Servidor.Dominio.DominioUseCases.solicitar_asignacion_rol_use_case import SolicitarAsignacionRolUseCase
from Servidor.Infraestructura.enviador_correo_memoria import EnviadorCorreoMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaciones_rol_memoria import (
    RepositorioAsignacionesRolMemoria,
)


def prueba_solicitar_y_confirmar_rol_profesor(
    repositorio_usuarios, usuario_registrado, hasher
):
    asignaciones = RepositorioAsignacionesRolMemoria()
    enviador = EnviadorCorreoMemoria()
    correo_secretaria = "secretaria@uclm.es"
    SolicitarAsignacionRolUseCase(
        repositorio_usuarios, asignaciones, enviador, timedelta(hours=24)
    ).ejecutar(
        usuario_registrado.email,
        Rol.SUPERADMINISTRADOR,
        "http://local",
        Rol.PROFESOR,
        correo_secretaria,
    )
    assert enviador.mensajes[-1][0] == correo_secretaria
    assert usuario_registrado.email in enviador.mensajes[-1][2]
    assert "?asignar-rol=" in enviador.mensajes[-1][2]
    token = enviador.mensajes[-1][2].split("?asignar-rol=")[1].split()[0]
    assert asignaciones.obtener(token) is None
    assert asignaciones.obtener(hash_token(token)) is not None
    guardado = ConfirmarAsignacionRolUseCase(repositorio_usuarios, asignaciones).ejecutar(token)
    assert guardado.rol == Rol.PROFESOR
    assert asignaciones.obtener(hash_token(token)) is None
