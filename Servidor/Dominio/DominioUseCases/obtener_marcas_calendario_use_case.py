from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento
from Servidor.Dominio.DominioQueries.obtener_marcas_calendario_query import ObtenerMarcasCalendarioQuery
from Servidor.Dominio.DominioServices.marcas_calendario import MarcaCalendario, SimboloCalendario
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos


class ObtenerMarcasCalendarioUseCase:
    def __init__(self, repositorio_eventos: RepositorioEventos, repositorio_asignaturas: RepositorioAsignaturas):
        self.repositorio_eventos = repositorio_eventos
        self.repositorio_asignaturas = repositorio_asignaturas

    def ejecutar(self, query: ObtenerMarcasCalendarioQuery) -> list[MarcaCalendario]:
        nombres = {asignatura.codigo: asignatura for asignatura in self.repositorio_asignaturas.obtener_todas()}
        por_dia: dict[int, list] = {}
        for evento in self.repositorio_eventos.obtener_todos():
            if evento.fecha.year != query.anio or evento.fecha.month != query.mes:
                continue
            por_dia.setdefault(evento.fecha.day, []).append(evento)
        marcas = []
        for dia in sorted(por_dia):
            ordenados = sorted(por_dia[dia], key=lambda evento: evento.tipo != TipoEvento.EXAMEN)
            simbolos = []
            for evento in ordenados:
                asignatura = nombres.get(evento.codigo)
                simbolos.append(
                    SimboloCalendario(
                        tipo="estrella" if evento.tipo == TipoEvento.EXAMEN else "punto",
                        codigo=evento.codigo,
                        nombre=asignatura.nombre if asignatura else evento.codigo,
                        nombre_ingles=asignatura.nombre_ingles if asignatura else evento.codigo,
                    )
                )
            marcas.append(MarcaCalendario(dia, simbolos))
        return marcas
