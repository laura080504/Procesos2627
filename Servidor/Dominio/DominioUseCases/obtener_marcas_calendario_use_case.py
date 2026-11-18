from Servidor.Dominio.DominioQueries.obtener_marcas_calendario_query import ObtenerMarcasCalendarioQuery
from Servidor.Dominio.DominioServices.marcas_calendario import MarcaCalendario, marcas_del_mes
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos


class ObtenerMarcasCalendarioUseCase:
    def __init__(self, repositorio_eventos: RepositorioEventos, repositorio_asignaturas: RepositorioAsignaturas):
        self.repositorio_eventos = repositorio_eventos
        self.repositorio_asignaturas = repositorio_asignaturas

    def ejecutar(self, query: ObtenerMarcasCalendarioQuery) -> list[MarcaCalendario]:
        asignaturas_por_codigo = {
            asignatura.codigo: asignatura for asignatura in self.repositorio_asignaturas.obtener_todas()
        }
        return marcas_del_mes(
            self.repositorio_eventos.obtener_todos(),
            asignaturas_por_codigo,
            query.anio,
            query.mes,
        )
