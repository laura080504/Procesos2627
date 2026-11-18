from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioQueries.listar_asignaturas_query import ListarAsignaturasQuery
from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas

_ORDEN_CURSO = {curso: posicion for posicion, curso in enumerate(CursoAsignatura)}


class ListarAsignaturasUseCase:
    def __init__(self, repositorio_asignaturas: RepositorioAsignaturas):
        self.repositorio_asignaturas = repositorio_asignaturas

    def ejecutar(self, query: ListarAsignaturasQuery) -> list[Asignatura]:
        asignaturas = sorted(
            self.repositorio_asignaturas.obtener_todas(),
            key=lambda asignatura: (_ORDEN_CURSO[asignatura.curso], asignatura.codigo),
        )
        busqueda = normalizar_texto(query.nombre)
        if not busqueda:
            return asignaturas
        return [asignatura for asignatura in asignaturas if _coincide(asignatura, busqueda)]


def _coincide(asignatura: Asignatura, busqueda: str) -> bool:
    return busqueda in normalizar_texto(asignatura.nombre) or busqueda in normalizar_texto(asignatura.nombre_ingles)
