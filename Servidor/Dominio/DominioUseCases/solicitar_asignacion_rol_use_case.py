from datetime import datetime, timedelta, timezone

from Servidor.Dominio.DominioEntities.asignacion_rol import AsignacionRol
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.correo_no_enviado import CorreoNoEnviado
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado
from Servidor.Dominio.DominioServices.token_seguro import hash_token, nuevo_token
from Servidor.Infraestructura.enviador_correo import EnviadorCorreo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaciones_rol import (
    RepositorioAsignacionesRol,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios


class SolicitarAsignacionRolUseCase:
    """Secretaría confirma por su propio correo el cambio de rol de un alumno."""

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_asignaciones: RepositorioAsignacionesRol,
        enviador: EnviadorCorreo,
        duracion: timedelta,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_asignaciones = repositorio_asignaciones
        self.enviador = enviador
        self.duracion = duracion

    def ejecutar(
        self,
        email_objetivo: str,
        solicitante_rol: Rol,
        url_base: str,
        rol_destino: Rol = Rol.PROFESOR,
        email_solicitante: str = "",
    ) -> None:
        if solicitante_rol != Rol.SUPERADMINISTRADOR:
            raise PermisoInsuficiente()
        if rol_destino != Rol.PROFESOR:
            raise PermisoInsuficiente()
        email = email_objetivo.strip().lower()
        destino_correo = (email_solicitante or "").strip().lower()
        if not destino_correo:
            raise PermisoInsuficiente()
        usuario = self.repositorio_usuarios.obtener_por_email(email)
        if usuario is None or usuario.estado == EstadoUsuario.ELIMINADO:
            raise UsuarioNoEncontrado(email)
        if usuario.rol != Rol.USUARIO:
            raise PermisoInsuficiente()

        self.repositorio_asignaciones.eliminar_por_email(email)
        token_plano = nuevo_token()
        self.repositorio_asignaciones.guardar(
            AsignacionRol(
                token=hash_token(token_plano),
                email=email,
                rol_destino=rol_destino,
                expira_en=datetime.now(timezone.utc) + self.duracion,
            )
        )
        enlace = f"{url_base.rstrip('/')}/?asignar-rol={token_plano}"
        cuerpo = (
            f"Has solicitado convertir a {usuario.nick} ({usuario.email}) en profesor.\n\n"
            "Abre este enlace para confirmar el cambio de rol (solo quien gestiona la cuenta "
            "oficial debe hacerlo):\n"
            f"{enlace}\n\n"
            "Si no pediste este cambio, ignora este mensaje. El enlace caduca en 24 horas."
        )
        try:
            self.enviador.enviar(
                destino_correo,
                "Confirma el cambio de rol a profesor",
                cuerpo,
            )
        except CorreoNoEnviado:
            self.repositorio_asignaciones.eliminar(hash_token(token_plano))
            raise
