from datetime import datetime, timezone

from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioExceptions.recuperacion_no_valida import RecuperacionNoValida
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado
from Servidor.Dominio.DominioServices.token_seguro import hash_token
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaciones_rol import (
    RepositorioAsignacionesRol,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios


class ConfirmarAsignacionRolUseCase:
    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_asignaciones: RepositorioAsignacionesRol,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_asignaciones = repositorio_asignaciones

    def ejecutar(self, token_plano: str) -> Usuario:
        asignacion = self.repositorio_asignaciones.obtener(hash_token(token_plano))
        if asignacion is None:
            raise RecuperacionNoValida()
        if asignacion.caducada(datetime.now(timezone.utc)):
            self.repositorio_asignaciones.eliminar(asignacion.token)
            raise RecuperacionNoValida()

        usuario = self.repositorio_usuarios.obtener_por_email(asignacion.email)
        if usuario is None or usuario.estado == EstadoUsuario.ELIMINADO:
            self.repositorio_asignaciones.eliminar(asignacion.token)
            raise UsuarioNoEncontrado(asignacion.email)
        if usuario.rol != Rol.USUARIO:
            self.repositorio_asignaciones.eliminar(asignacion.token)
            raise PermisoInsuficiente()

        usuario.rol = asignacion.rol_destino
        usuario.delegado_curso = None
        self.repositorio_usuarios.actualizar(usuario)
        self.repositorio_asignaciones.eliminar(asignacion.token)
        guardado = self.repositorio_usuarios.obtener_por_email(usuario.email)
        if guardado is None:
            raise RuntimeError(f"No se ha podido actualizar el rol de {usuario.email}")
        return guardado
