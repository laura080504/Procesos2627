from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_avisos_secretaria import (
    RepositorioAvisosSecretaria,
)


class EliminarAvisoSecretariaUseCase:
    def __init__(self, repositorio: RepositorioAvisosSecretaria):
        self.repositorio = repositorio

    def ejecutar(self, aviso_id: str, solicitante_rol: Rol) -> None:
        if solicitante_rol != Rol.SUPERADMINISTRADOR:
            raise PermisoInsuficiente()
        if not self.repositorio.eliminar(aviso_id):
            raise EstadoNoValido("No existe ese aviso de secretaría")
