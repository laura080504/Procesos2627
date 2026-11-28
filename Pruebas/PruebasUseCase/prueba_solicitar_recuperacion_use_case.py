from datetime import timedelta

from Servidor.Dominio.DominioCommands.solicitar_recuperacion_command import SolicitarRecuperacionCommand
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.proveedor_auth import ProveedorAuth
from Servidor.Dominio.DominioServices.token_seguro import hash_token
from Servidor.Dominio.DominioUseCases.solicitar_recuperacion_use_case import SolicitarRecuperacionUseCase
from Servidor.Infraestructura.enviador_correo_memoria import EnviadorCorreoMemoria


def _use_case(repositorio_usuarios, repositorio_recuperaciones, enviador=None):
    return SolicitarRecuperacionUseCase(
        repositorio_usuarios,
        repositorio_recuperaciones,
        enviador or EnviadorCorreoMemoria(),
        timedelta(minutes=15),
    )


def prueba_email_conocido_guarda_hash_y_envia_enlace(
    repositorio_usuarios, usuario_registrado, repositorio_recuperaciones
):
    enviador = EnviadorCorreoMemoria()
    use_case = _use_case(repositorio_usuarios, repositorio_recuperaciones, enviador)
    assert use_case.ejecutar(SolicitarRecuperacionCommand(usuario_registrado.email), "http://127.0.0.1:8000") is None
    assert "?recuperar=" in enviador.mensajes[-1][2]
    token_plano = enviador.mensajes[-1][2].split("?recuperar=")[1].split()[0]
    assert repositorio_recuperaciones.obtener(token_plano) is None
    assert repositorio_recuperaciones.obtener(hash_token(token_plano)) is not None


def prueba_email_desconocido_no_revela_nada(repositorio_usuarios, repositorio_recuperaciones):
    enviador = EnviadorCorreoMemoria()
    use_case = _use_case(repositorio_usuarios, repositorio_recuperaciones, enviador)
    assert use_case.ejecutar(SolicitarRecuperacionCommand("nadie@ejemplo.com"), "http://local") is None
    assert repositorio_recuperaciones._recuperaciones == {}
    assert enviador.mensajes == []


def prueba_cuenta_solo_oauth_recibe_aviso_sin_token(
    repositorio_usuarios, usuario_registrado, repositorio_recuperaciones
):
    enviador = EnviadorCorreoMemoria()
    usuario_registrado.contrasena_hash = None
    usuario_registrado.proveedores = (ProveedorAuth.GOOGLE.value,)
    repositorio_usuarios.actualizar(usuario_registrado)
    use_case = _use_case(repositorio_usuarios, repositorio_recuperaciones, enviador)
    use_case.ejecutar(SolicitarRecuperacionCommand(usuario_registrado.email), "http://local")
    assert repositorio_recuperaciones._recuperaciones == {}
    assert "Google o UCLM" in enviador.mensajes[-1][2]


def prueba_usuario_eliminado_no_recibe_correo(
    repositorio_usuarios, usuario_registrado, repositorio_recuperaciones
):
    enviador = EnviadorCorreoMemoria()
    use_case = _use_case(repositorio_usuarios, repositorio_recuperaciones, enviador)
    usuario_registrado.estado = EstadoUsuario.ELIMINADO
    use_case.ejecutar(SolicitarRecuperacionCommand(usuario_registrado.email), "http://local")
    assert repositorio_recuperaciones._recuperaciones == {}
    assert enviador.mensajes == []
