from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado
from Servidor.Dominio.DominioExceptions.usuario_ya_existe import UsuarioYaExiste
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones import (
    RepositorioRecuperaciones,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios


class EditarAlumnoSecretariaUseCase:
    """Secretaría cambia nick y correo de un alumno, y mueve sesión y matrícula."""

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_sesiones: RepositorioSesiones,
        repositorio_recuperaciones: RepositorioRecuperaciones,
        repositorio_matriculas: RepositorioMatriculas,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_sesiones = repositorio_sesiones
        self.repositorio_recuperaciones = repositorio_recuperaciones
        self.repositorio_matriculas = repositorio_matriculas

    def ejecutar(self, email: str, email_nuevo: str, nick: str, solicitante_rol: Rol) -> Usuario:
        if solicitante_rol != Rol.SUPERADMINISTRADOR:
            raise PermisoInsuficiente()
        actual = email.strip().lower()
        nuevo = email_nuevo.strip().lower()
        objetivo = self.repositorio_usuarios.obtener_por_email(actual)
        if objetivo is None or objetivo.estado == EstadoUsuario.ELIMINADO:
            raise UsuarioNoEncontrado(actual)
        if objetivo.rol != Rol.USUARIO:
            raise PermisoInsuficiente()
        if nuevo != actual and self.repositorio_usuarios.obtener_por_email(nuevo) is not None:
            raise UsuarioYaExiste(nuevo)
        objetivo.nick = nick.strip()
        if nuevo != actual:
            objetivo.email = nuevo
            self.repositorio_usuarios.cambiar_email(actual, objetivo)
            self.repositorio_sesiones.actualizar_email(actual, nuevo)
            self.repositorio_recuperaciones.actualizar_email(actual, nuevo)
            self.repositorio_matriculas.cambiar_email(actual, nuevo)
        else:
            self.repositorio_usuarios.actualizar(objetivo)
        guardado = self.repositorio_usuarios.obtener_por_email(nuevo)
        if guardado is None:
            raise RuntimeError(f"No se han podido guardar los datos de {nuevo}")
        return guardado
