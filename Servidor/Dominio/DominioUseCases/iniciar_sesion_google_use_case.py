from datetime import datetime, timedelta, timezone

from Servidor.Dominio.DominioEntities.sesion import Sesion
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.proveedor_auth import ProveedorAuth
from Servidor.Dominio.DominioExceptions.cuenta_eliminada import CuentaEliminada
from Servidor.Dominio.DominioExceptions.cuenta_pendiente import CuentaPendiente
from Servidor.Dominio.DominioExceptions.oauth_no_valido import OauthNoValido
from Servidor.Dominio.DominioResults.inicio_sesion_resultado import InicioSesionResultado
from Servidor.Dominio.DominioServices.matriculas_muestra import asegurar_matricula_de
from Servidor.Dominio.DominioServices.token_seguro import nuevo_token
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_confirmaciones import RepositorioConfirmaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios


class IniciarSesionGoogleUseCase:
    """Login federado (Google o UCLM). Requiere email verificado por el IdP."""

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_sesiones: RepositorioSesiones,
        duracion_sesion: timedelta,
        repositorio_confirmaciones: RepositorioConfirmaciones | None = None,
        repositorio_matriculas: RepositorioMatriculas | None = None,
        proveedor: str = ProveedorAuth.GOOGLE.value,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_sesiones = repositorio_sesiones
        self.duracion_sesion = duracion_sesion
        self.repositorio_confirmaciones = repositorio_confirmaciones
        self.repositorio_matriculas = repositorio_matriculas
        self.proveedor = proveedor

    def ejecutar(
        self,
        email: str,
        nombre: str,
        email_verificado: bool = False,
        recordar: bool = False,
        duracion_sesion: timedelta | None = None,
    ) -> InicioSesionResultado:
        email = email.strip().lower()
        if "@" not in email:
            raise OauthNoValido()
        if not email_verificado:
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
                    contrasena_hash=None,
                    estado=EstadoUsuario.ACTIVO,
                    proveedores=(self.proveedor,),
                )
            )
            usuario = self.repositorio_usuarios.obtener_por_email(email)
        elif usuario.estado == EstadoUsuario.PENDIENTE:
            # Evita account takeover: no activar ni vincular una cuenta local sin verificar.
            raise CuentaPendiente(email)
        else:
            usuario = usuario.con_proveedor(self.proveedor)
            self.repositorio_usuarios.actualizar(usuario)
            usuario = self.repositorio_usuarios.obtener_por_email(email)

        if usuario is None:
            raise RuntimeError(f"No se ha podido guardar la sesión de {email}")
        if self.repositorio_confirmaciones is not None:
            self.repositorio_confirmaciones.eliminar_por_email(email)
        if self.repositorio_matriculas is not None:
            asegurar_matricula_de(self.repositorio_matriculas, email)

        duracion = duracion_sesion or self.duracion_sesion
        sesion = Sesion(
            token=nuevo_token(),
            email=email,
            expira_en=datetime.now(timezone.utc) + duracion,
        )
        self.repositorio_sesiones.guardar(sesion)
        return InicioSesionResultado(sesion=sesion, usuario=usuario)
