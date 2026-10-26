from fastapi import Depends

from Servidor.ApiRest.ApiRestDependencies.repositorio_dependencies import (
    obtener_repositorio_asignaturas,
    obtener_repositorio_eventos,
    obtener_repositorio_matriculas,
)
from Servidor.Dominio.DominioUseCases.listar_asignaturas_use_case import ListarAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.obtener_marcas_calendario_use_case import ObtenerMarcasCalendarioUseCase
from Servidor.Dominio.DominioUseCases.obtener_matricula_use_case import ObtenerMatriculaUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas


def crear_listar_asignaturas_use_case(
    repositorio_asignaturas: RepositorioAsignaturas = Depends(obtener_repositorio_asignaturas),
) -> ListarAsignaturasUseCase:
    return ListarAsignaturasUseCase(repositorio_asignaturas)


def crear_obtener_marcas_calendario_use_case(
    repositorio_eventos: RepositorioEventos = Depends(obtener_repositorio_eventos),
    repositorio_asignaturas: RepositorioAsignaturas = Depends(obtener_repositorio_asignaturas),
) -> ObtenerMarcasCalendarioUseCase:
    return ObtenerMarcasCalendarioUseCase(repositorio_eventos, repositorio_asignaturas)


def crear_obtener_matricula_use_case(
    repositorio_matriculas: RepositorioMatriculas = Depends(obtener_repositorio_matriculas),
    repositorio_asignaturas: RepositorioAsignaturas = Depends(obtener_repositorio_asignaturas),
) -> ObtenerMatriculaUseCase:
    return ObtenerMatriculaUseCase(repositorio_matriculas, repositorio_asignaturas)
