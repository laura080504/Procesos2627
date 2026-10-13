from datetime import datetime, timedelta, timezone

import pytest

from Pruebas.conftest import CONTRASENA
from Servidor.Dominio.DominioCommands.editar_datos_command import EditarDatosCommand
from Servidor.Dominio.DominioEntities.sesion import Sesion
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado
from Servidor.Dominio.DominioExceptions.usuario_ya_existe import UsuarioYaExiste
from Servidor.Dominio.DominioUseCases.editar_datos_use_case import EditarDatosUseCase


@pytest.fixture
def use_case(repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones, hasher):
    return EditarDatosUseCase(
        repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones, hasher
    )


def prueba_cambia_nick_sin_tocar_contrasena(use_case, usuario_registrado, repositorio_usuarios, hasher):
    actualizado = use_case.ejecutar(
        EditarDatosCommand(usuario_registrado.email, usuario_registrado.email, "nuevo-nick")
    )
    guardado = repositorio_usuarios.obtener_por_email(usuario_registrado.email)
    assert actualizado.nick == "nuevo-nick"
    assert guardado.nick == "nuevo-nick"
    assert hasher.verificar(CONTRASENA, guardado.contrasena_hash)


def prueba_cambia_contrasena(use_case, usuario_registrado, repositorio_usuarios, hasher):
    use_case.ejecutar(
        EditarDatosCommand(usuario_registrado.email, usuario_registrado.email, "laura", "nueva-segura")
    )
    guardado = repositorio_usuarios.obtener_por_email(usuario_registrado.email)
    assert hasher.verificar("nueva-segura", guardado.contrasena_hash)
    assert not hasher.verificar(CONTRASENA, guardado.contrasena_hash)


def prueba_cambia_email_y_mantiene_la_sesion(
    use_case, usuario_registrado, repositorio_usuarios, repositorio_sesiones
):
    sesion = Sesion(
        "token-sesion",
        usuario_registrado.email,
        datetime.now(timezone.utc) + timedelta(hours=1),
    )
    repositorio_sesiones.guardar(sesion)
    use_case.ejecutar(EditarDatosCommand(usuario_registrado.email, "nuevo@ejemplo.com", "laura"))
    assert repositorio_usuarios.obtener_por_email("laura@ejemplo.com") is None
    guardado = repositorio_usuarios.obtener_por_email("nuevo@ejemplo.com")
    assert guardado is not None
    assert guardado.nick == "laura"
    assert repositorio_sesiones.obtener("token-sesion").email == "nuevo@ejemplo.com"


def prueba_no_permite_un_email_ya_usado(use_case, usuario_registrado, administrador):
    with pytest.raises(UsuarioYaExiste):
        use_case.ejecutar(
            EditarDatosCommand(usuario_registrado.email, administrador.email, "laura")
        )
    assert usuario_registrado.email == "laura@ejemplo.com"


def prueba_eliminado_no_puede_editar(use_case, usuario_registrado, repositorio_usuarios):
    usuario_registrado.estado = EstadoUsuario.ELIMINADO
    repositorio_usuarios.actualizar(usuario_registrado)
    with pytest.raises(UsuarioNoEncontrado):
        use_case.ejecutar(
            EditarDatosCommand(usuario_registrado.email, usuario_registrado.email, "otro")
        )
