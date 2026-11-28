from datetime import datetime, timedelta, timezone

from Servidor.Dominio.DominioCommands.solicitar_recuperacion_command import SolicitarRecuperacionCommand
from Servidor.Dominio.DominioEntities.recuperacion import Recuperacion
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioExceptions.correo_no_enviado import CorreoNoEnviado
from Servidor.Dominio.DominioServices.token_seguro import hash_token, nuevo_token
from Servidor.Infraestructura.enviador_correo import EnviadorCorreo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones import RepositorioRecuperaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios


class SolicitarRecuperacionUseCase:
    """Siempre responde igual hacia fuera; el token solo viaja por correo (hasheado en BBDD)."""

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_recuperaciones: RepositorioRecuperaciones,
        enviador: EnviadorCorreo,
        duracion: timedelta,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_recuperaciones = repositorio_recuperaciones
        self.enviador = enviador
        self.duracion = duracion

    def ejecutar(self, command: SolicitarRecuperacionCommand, url_base: str) -> None:
        email = command.email.strip().lower()
        usuario = self.repositorio_usuarios.obtener_por_email(email)
        if usuario is None or usuario.estado == EstadoUsuario.ELIMINADO:
            return

        if usuario.solo_oauth():
            cuerpo = (
                f"Hola {usuario.nick}.\n\n"
                "Has pedido recuperar la contraseña, pero esta cuenta entra con Google o UCLM "
                "(no tiene contraseña local).\n"
                "Usa el botón correspondiente en la pantalla de inicio de sesión.\n"
            )
            try:
                self.enviador.enviar(email, "Tu cuenta usa Google o UCLM", cuerpo)
            except CorreoNoEnviado:
                raise
            return

        if not usuario.contrasena_hash:
            return

        self.repositorio_recuperaciones.eliminar_por_email(email)
        token_plano = nuevo_token()
        recuperacion = Recuperacion(
            token=hash_token(token_plano),
            email=email,
            expira_en=datetime.now(timezone.utc) + self.duracion,
        )
        self.repositorio_recuperaciones.guardar(recuperacion)
        enlace = f"{url_base.rstrip('/')}/?recuperar={token_plano}"
        cuerpo = (
            f"Hola {usuario.nick}.\n\n"
            "Abre este enlace para elegir una contraseña nueva:\n"
            f"{enlace}\n\n"
            "Si no pediste recuperar la cuenta, ignora este correo. "
            "El enlace caduca en 15 minutos."
        )
        try:
            self.enviador.enviar(email, "Recupera tu contraseña", cuerpo)
        except CorreoNoEnviado:
            self.repositorio_recuperaciones.eliminar(recuperacion.token)
            raise
