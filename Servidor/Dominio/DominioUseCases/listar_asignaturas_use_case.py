import unicodedata

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioQueries.listar_asignaturas_query import ListarAsignaturasQuery
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas

_ORDEN_CURSO = {curso: posicion for posicion, curso in enumerate(CursoAsignatura)}


def _plano(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFD", texto.casefold().strip())
    return "".join(letra for letra in descompuesto if unicodedata.category(letra) != "Mn")


class ListarAsignaturasUseCase:
    def __init__(self, repositorio_asignaturas: RepositorioAsignaturas):
        self.repositorio_asignaturas = repositorio_asignaturas

    def ejecutar(self, query: ListarAsignaturasQuery) -> list[Asignatura]:
        asignaturas = sorted(
            self.repositorio_asignaturas.obtener_todas(),
            key=lambda asignatura: (_ORDEN_CURSO[asignatura.curso], asignatura.codigo),
        )
        busqueda = _plano(query.nombre)
        if not busqueda:
            return asignaturas
        return [
            asignatura
            for asignatura in asignaturas
            if busqueda in _plano(asignatura.nombre) or busqueda in _plano(asignatura.nombre_ingles)
        ]
