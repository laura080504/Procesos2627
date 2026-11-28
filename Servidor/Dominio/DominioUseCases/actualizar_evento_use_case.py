from Servidor.Dominio.DominioCommands.actualizar_evento_command import ActualizarEventoCommand
from Servidor.Dominio.DominioEntities.evento import Evento, identidad_evento
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia import RepositorioDocencia
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos


class ActualizarEventoUseCase:
    def __init__(
        self,
        repositorio_eventos: RepositorioEventos,
        repositorio_asignaturas: RepositorioAsignaturas,
        repositorio_docencia: RepositorioDocencia | None = None,
    ):
        self.repositorio_eventos = repositorio_eventos
        self.repositorio_asignaturas = repositorio_asignaturas
        self.repositorio_docencia = repositorio_docencia

    def ejecutar(self, command: ActualizarEventoCommand) -> Evento:
        if command.solicitante_rol not in (Rol.PROFESOR, Rol.SUPERADMINISTRADOR):
            raise PermisoInsuficiente()

        existente = self.repositorio_eventos.obtener_por_id(command.evento_id)
        if existente is None:
            raise EstadoNoValido("No existe ese examen o entrega")

        codigo = command.codigo.strip()
        asignatura = next(
            (item for item in self.repositorio_asignaturas.obtener_todas() if item.codigo == codigo),
            None,
        )
        if asignatura is None:
            raise EstadoNoValido(f"No existe la asignatura {codigo}")

        if command.solicitante_rol == Rol.PROFESOR:
            codigos_docencia = (
                self.repositorio_docencia.obtener_codigos(command.solicitante_email)
                if self.repositorio_docencia is not None
                else []
            )
            if existente.codigo not in codigos_docencia or codigo not in codigos_docencia:
                raise PermisoInsuficiente()

        lugar = command.lugar.strip() if command.lugar else None
        if not lugar:
            lugar = None
        actualizado = Evento(
            fecha=command.fecha,
            codigo=codigo,
            tipo=command.tipo,
            hora=command.hora.strip(),
            lugar=lugar,
            id=identidad_evento(existente),
        )
        self.repositorio_eventos.eliminar(command.evento_id)
        self.repositorio_eventos.guardar(actualizado)
        return actualizado
