import secrets
from datetime import datetime, timedelta, timezone

from Servidor.Dominio.DominioEntities.confirmacion import Confirmacion
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioExceptions.correo_no_enviado import CorreoNoEnviado
from Servidor.Dominio.DominioExceptions.cuenta_eliminada import CuentaEliminada
from Servidor.Dominio.DominioExceptions.cuenta_ya_activa import CuentaYaActiva
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado
from Servidor.Infraestructura.enviador_correo import EnviadorCorreo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_confirmaciones import RepositorioConfirmaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios


class EmitirConfirmacionUseCase:
    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_confirmaciones: RepositorioConfirmaciones,
        enviador: EnviadorCorreo,
        duracion: timedelta,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_confirmaciones = repositorio_confirmaciones
        self.enviador = enviador
        self.duracion = duracion

    def ejecutar(self, email: str, url_base: str) -> Confirmacion:
        email = email.strip().lower()
        usuario = self.repositorio_usuarios.obtener_por_email(email)
        if usuario is None:
            raise UsuarioNoEncontrado(email)
        if usuario.estado == EstadoUsuario.ELIMINADO:
            raise CuentaEliminada(email)
        if usuario.estado == EstadoUsuario.ACTIVO:
            raise CuentaYaActiva()
        self.repositorio_confirmaciones.eliminar_por_email(email)
        confirmacion = Confirmacion(
            token=secrets.token_urlsafe(32),
            email=email,
            expira_en=datetime.now(timezone.utc) + self.duracion,
        )
        self.repositorio_confirmaciones.guardar(confirmacion)
        enlace = f"{url_base.rstrip('/')}/?confirmar={confirmacion.token}"
        cuerpo = (
            f"Hola {usuario.nick}.\n\n"
            "Abre este enlace para confirmar tu cuenta:\n"
            f"{enlace}\n\n"
            "Hasta que lo abras, la cuenta queda pendiente y no puedes iniciar sesión. "
            "El enlace caduca en 24 horas."
        )
        try:
            self.enviador.enviar(email, "Confirma tu cuenta", cuerpo)
        except CorreoNoEnviado:
            self.repositorio_confirmaciones.eliminar(confirmacion.token)
            raise
        return confirmacion
