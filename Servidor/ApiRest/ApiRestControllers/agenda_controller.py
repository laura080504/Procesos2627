from datetime import date

from fastapi import APIRouter, Depends, Query

from Servidor.ApiRest.ApiRestDependencies.agenda_dependencies import (
    crear_listar_asignaturas_use_case,
    crear_obtener_marcas_calendario_use_case,
    crear_obtener_matricula_use_case,
)
from Servidor.ApiRest.ApiRestDependencies.auth_dependencies import obtener_usuario_actual
from Servidor.ApiRest.ApiRestSchemas.asignatura_salida import AsignaturaSalida
from Servidor.ApiRest.ApiRestSchemas.marca_calendario_salida import MarcaCalendarioSalida
from Servidor.ApiRest.ApiRestSchemas.matricula_salida import MatriculaSalida
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioQueries.listar_asignaturas_query import ListarAsignaturasQuery
from Servidor.Dominio.DominioQueries.obtener_marcas_calendario_query import ObtenerMarcasCalendarioQuery
from Servidor.Dominio.DominioUseCases.listar_asignaturas_use_case import ListarAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.obtener_marcas_calendario_use_case import ObtenerMarcasCalendarioUseCase
from Servidor.Dominio.DominioUseCases.obtener_matricula_use_case import ObtenerMatriculaUseCase

router = APIRouter(tags=["agenda"])


@router.get("/api/asignaturas", response_model=list[AsignaturaSalida])
def listar_asignaturas(
    nombre: str = "",
    _: Usuario = Depends(obtener_usuario_actual),
    use_case: ListarAsignaturasUseCase = Depends(crear_listar_asignaturas_use_case),
):
    return use_case.ejecutar(ListarAsignaturasQuery(nombre=nombre))


@router.get("/api/matricula", response_model=MatriculaSalida)
def obtener_matricula(
    nombre: str = "",
    usuario: Usuario = Depends(obtener_usuario_actual),
    use_case: ObtenerMatriculaUseCase = Depends(crear_obtener_matricula_use_case),
):
    return use_case.ejecutar(usuario.email, nombre)


@router.get("/api/agenda/marcas", response_model=list[MarcaCalendarioSalida])
def obtener_marcas(
    anio: int | None = None,
    mes: int | None = Query(default=None, ge=1, le=12),
    _: Usuario = Depends(obtener_usuario_actual),
    use_case: ObtenerMarcasCalendarioUseCase = Depends(crear_obtener_marcas_calendario_use_case),
):
    hoy = date.today()
    return use_case.ejecutar(ObtenerMarcasCalendarioQuery(anio or hoy.year, mes or hoy.month))
