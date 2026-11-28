from Servidor.Dominio.DominioCommands.eliminar_evento_command import EliminarEventoCommand
from Servidor.Dominio.DominioEntities.evento import Evento
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia import RepositorioDocencia
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos


class EliminarEventoUseCase:
    def __init__(
        self,
        repositorio_eventos: RepositorioEventos,
        repositorio_docencia: RepositorioDocencia | None = None,
    ):
        self.repositorio_eventos = repositorio_eventos
        self.repositorio_docencia = repositorio_docencia

    def ejecutar(self, command: EliminarEventoCommand) -> Evento:
        if command.solicitante_rol not in (Rol.PROFESOR, Rol.SUPERADMINISTRADOR):
            raise PermisoInsuficiente()

        existente = self.repositorio_eventos.obtener_por_id(command.evento_id)
        if existente is None:
            raise EstadoNoValido("No existe ese examen o entrega")

        if command.solicitante_rol == Rol.PROFESOR:
            codigos_docencia = (
                self.repositorio_docencia.obtener_codigos(command.solicitante_email)
                if self.repositorio_docencia is not None
                else []
            )
            if existente.codigo not in codigos_docencia:
                raise PermisoInsuficiente()

        if not self.repositorio_eventos.eliminar(command.evento_id):
            raise EstadoNoValido("No existe ese examen o entrega")
        return existente