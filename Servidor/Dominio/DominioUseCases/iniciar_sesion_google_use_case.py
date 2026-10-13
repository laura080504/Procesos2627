import secrets
from datetime import datetime, timedelta, timezone

from Servidor.Dominio.DominioEntities.sesion import Sesion
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioExceptions.cuenta_eliminada import CuentaEliminada
from Servidor.Dominio.DominioExceptions.oauth_no_valido import OauthNoValido
from Servidor.Dominio.DominioResults.inicio_sesion_resultado import InicioSesionResultado
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_confirmaciones import RepositorioConfirmaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios


class IniciarSesionGoogleUseCase:
    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_sesiones: RepositorioSesiones,
        hasher: HasherContrasenas,
        duracion_sesion: timedelta,
        repositorio_confirmaciones: RepositorioConfirmaciones | None = None,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_sesiones = repositorio_sesiones
        self.hasher = hasher
        self.duracion_sesion = duracion_sesion
        self.repositorio_confirmaciones = repositorio_confirmaciones

    def ejecutar(self, email: str, nombre: str) -> InicioSesionResultado:
        email = email.strip().lower()
        if "@" not in email:
            raise OauthNoValido()
        usuario = self.repositorio_usuarios.obtener_por_email(email)
        if usuario is not None and usuario.estado == EstadoUsuario.ELIMINADO:
            raise CuentaEliminada(email)
        if usuario is None:
            nick = nombre.strip()[:30] or email.split("@")[0][:30] or "usuario"
            self.repositorio_usuarios.insertar(
                Usuario(
                    email=email,
                    nick=nick,
                    contrasena_hash=self.hasher.hashear(secrets.token_urlsafe(32)),
                    estado=EstadoUsuario.ACTIVO,
                )
            )
            usuario = self.repositorio_usuarios.obtener_por_email(email)
        elif usuario.estado == EstadoUsuario.PENDIENTE:
            usuario.estado = EstadoUsuario.ACTIVO
            self.repositorio_usuarios.actualizar(usuario)
            usuario = self.repositorio_usuarios.obtener_por_email(email)
        if usuario is None:
            raise RuntimeError(f"No se ha podido guardar la sesión de {email}")
        if self.repositorio_confirmaciones is not None:
            self.repositorio_confirmaciones.eliminar_por_email(email)
        sesion = Sesion(
            token=secrets.token_urlsafe(32),
            email=email,
            expira_en=datetime.now(timezone.utc) + self.duracion_sesion,
        )
        self.repositorio_sesiones.guardar(sesion)
        return InicioSesionResultado(sesion=sesion, usuario=usuario)
