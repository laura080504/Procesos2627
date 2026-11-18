from Servidor.Dominio.DominioCommands.crear_evento_command import CrearEventoCommand
from Servidor.Dominio.DominioEntities.evento import Evento
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos


class CrearEventoUseCase:
    def __init__(self, repositorio_eventos: RepositorioEventos, repositorio_asignaturas: RepositorioAsignaturas):
        self.repositorio_eventos = repositorio_eventos
        self.repositorio_asignaturas = repositorio_asignaturas

    def ejecutar(self, command: CrearEventoCommand) -> Evento:
        if command.solicitante_rol not in (Rol.PROFESOR, Rol.SUPERADMINISTRADOR):
            raise PermisoInsuficiente()

        codigo = command.codigo.strip()
        asignatura = next(
            (item for item in self.repositorio_asignaturas.obtener_todas() if item.codigo == codigo),
            None,
        )
        if asignatura is None:
            raise EstadoNoValido(f"No existe la asignatura {codigo}")

        lugar = command.lugar.strip() if command.lugar else None
        if not lugar:
            lugar = None
        evento = Evento(
            fecha=command.fecha,
            codigo=codigo,
            tipo=command.tipo,
            hora=command.hora.strip(),
            lugar=lugar,
        )
        self.repositorio_eventos.guardar(evento)
        return evento
