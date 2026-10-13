from datetime import datetime, timezone

from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioExceptions.confirmacion_no_valida import ConfirmacionNoValida
from Servidor.Dominio.DominioExceptions.cuenta_eliminada import CuentaEliminada
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_confirmaciones import RepositorioConfirmaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios


class ConfirmarCuentaUseCase:
    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_confirmaciones: RepositorioConfirmaciones,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_confirmaciones = repositorio_confirmaciones

    def ejecutar(self, token: str) -> Usuario:
        confirmacion = self.repositorio_confirmaciones.obtener(token.strip())
        if confirmacion is None or confirmacion.caducada(datetime.now(timezone.utc)):
            if confirmacion is not None:
                self.repositorio_confirmaciones.eliminar(confirmacion.token)
            raise ConfirmacionNoValida()
        usuario = self.repositorio_usuarios.obtener_por_email(confirmacion.email)
        self.repositorio_confirmaciones.eliminar(confirmacion.token)
        if usuario is None:
            raise ConfirmacionNoValida()
        if usuario.estado == EstadoUsuario.ELIMINADO:
            raise CuentaEliminada(usuario.email)
        usuario.estado = EstadoUsuario.ACTIVO
        self.repositorio_usuarios.actualizar(usuario)
        guardado = self.repositorio_usuarios.obtener_por_email(usuario.email)
        if guardado is None or guardado.estado != EstadoUsuario.ACTIVO:
            raise RuntimeError(f"No se ha podido confirmar la cuenta {usuario.email}")
        return guardado
