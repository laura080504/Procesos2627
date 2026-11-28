from datetime import date

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import JSONResponse

from Servidor.ApiRest.ApiRestDependencies.agenda_dependencies import (
    crear_actualizar_evento_use_case,
    crear_crear_evento_use_case,
    crear_eliminar_evento_use_case,
    crear_guardar_expediente_use_case,
    crear_guardar_matricula_use_case,
    crear_listar_asignaturas_use_case,
    crear_obtener_destinatarios_aviso_use_case,
    crear_obtener_expediente_use_case,
    crear_obtener_marcas_calendario_use_case,
    crear_obtener_matricula_use_case,
    invalidar_cache_marcas,
)
from Servidor.ApiRest.ApiRestDependencies.auth_dependencies import obtener_usuario_actual
from Servidor.ApiRest.ApiRestDependencies.repositorio_dependencies import obtener_repositorio_asignaturas
from Servidor.ApiRest.ApiRestSchemas.asignatura_salida import AsignaturaSalida
from Servidor.ApiRest.ApiRestSchemas.evento_entrada import EventoEntrada
from Servidor.ApiRest.ApiRestSchemas.evento_salida import EventoSalida
from Servidor.ApiRest.ApiRestSchemas.expediente_entrada import ExpedienteEntrada
from Servidor.ApiRest.ApiRestSchemas.expediente_salida import ExpedienteSalida
from Servidor.ApiRest.ApiRestSchemas.marca_calendario_salida import MarcaCalendarioSalida, MarcasRangoSalida
from Servidor.ApiRest.ApiRestSchemas.matricula_entrada import MatriculaEntrada
from Servidor.ApiRest.ApiRestSchemas.matricula_salida import MatriculaSalida
from Servidor.ApiWs.gestor_conexiones import gestor
from Servidor.Dominio.DominioCommands.actualizar_evento_command import ActualizarEventoCommand
from Servidor.Dominio.DominioCommands.crear_evento_command import CrearEventoCommand
from Servidor.Dominio.DominioCommands.eliminar_evento_command import EliminarEventoCommand
from Servidor.Dominio.DominioEntities.evento import identidad_evento
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioQueries.listar_asignaturas_query import ListarAsignaturasQuery
from Servidor.Dominio.DominioQueries.obtener_marcas_calendario_query import ObtenerMarcasCalendarioQuery
from Servidor.Dominio.DominioUseCases.actualizar_evento_use_case import ActualizarEventoUseCase
from Servidor.Dominio.DominioUseCases.crear_evento_use_case import CrearEventoUseCase
from Servidor.Dominio.DominioUseCases.eliminar_evento_use_case import EliminarEventoUseCase
from Servidor.Dominio.DominioUseCases.guardar_expediente_use_case import (
    CalificacionEntrada,
    GuardarExpedienteUseCase,
)
from Servidor.Dominio.DominioUseCases.guardar_matricula_use_case import (
    AsignaturaMatriculaEntrada,
    GuardarMatriculaUseCase,
)
from Servidor.Dominio.DominioUseCases.listar_asignaturas_use_case import ListarAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.obtener_destinatarios_aviso_use_case import (
    ObtenerDestinatariosAvisoUseCase,
)
from Servidor.Dominio.DominioUseCases.obtener_expediente_use_case import ObtenerExpedienteUseCase
from Servidor.Dominio.DominioUseCases.obtener_marcas_calendario_use_case import ObtenerMarcasCalendarioUseCase
from Servidor.Dominio.DominioUseCases.obtener_matricula_use_case import ObtenerMatriculaUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas

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


@router.put("/api/matricula", response_model=MatriculaSalida)
def guardar_matricula(
    cuerpo: MatriculaEntrada,
    usuario: Usuario = Depends(obtener_usuario_actual),
    use_case: GuardarMatriculaUseCase = Depends(crear_guardar_matricula_use_case),
):
    try:
        return use_case.ejecutar(
            usuario.email,
            [
                AsignaturaMatriculaEntrada(asignatura.codigo, asignatura.grupo)
                for asignatura in cuerpo.asignaturas
            ],
        )
    except EstadoNoValido as error:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(error)})


@router.get("/api/expediente", response_model=ExpedienteSalida)
def obtener_expediente(
    usuario: Usuario = Depends(obtener_usuario_actual),
    use_case: ObtenerExpedienteUseCase = Depends(crear_obtener_expediente_use_case),
):
    # TODO(secretaría): importar notas oficiales UCLM cuando haya API.
    return use_case.ejecutar(usuario.email)


@router.put("/api/expediente", response_model=ExpedienteSalida)
def guardar_expediente(
    cuerpo: ExpedienteEntrada,
    usuario: Usuario = Depends(obtener_usuario_actual),
    use_case: GuardarExpedienteUseCase = Depends(crear_guardar_expediente_use_case),
):
    try:
        # Si solo llega intensificación (sin lista de notas), no se tocan las calificaciones.
        solo_rama = cuerpo.intensificacion is not None and not cuerpo.calificaciones
        return use_case.ejecutar(
            usuario.email,
            [
                CalificacionEntrada(item.codigo, item.nota, item.convalidada)
                for item in cuerpo.calificaciones
            ],
            cuerpo.intensificacion,
            actualizar_calificaciones=not solo_rama,
        )
    except EstadoNoValido as error:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(error)})


@router.get("/api/agenda/marcas", response_model=list[MarcaCalendarioSalida])
def obtener_marcas(
    anio: int | None = None,
    mes: int | None = Query(default=None, ge=1, le=12),
    _: Usuario = Depends(obtener_usuario_actual),
    use_case: ObtenerMarcasCalendarioUseCase = Depends(crear_obtener_marcas_calendario_use_case),
):
    hoy = date.today()
    return use_case.ejecutar(ObtenerMarcasCalendarioQuery(anio or hoy.year, mes or hoy.month))


@router.get("/api/agenda/marcas-rango", response_model=MarcasRangoSalida)
def obtener_marcas_rango(
    anio: int | None = None,
    mes: int | None = Query(default=None, ge=1, le=12),
    cantidad: int = Query(default=1, ge=1, le=14),
    _: Usuario = Depends(obtener_usuario_actual),
    use_case: ObtenerMarcasCalendarioUseCase = Depends(crear_obtener_marcas_calendario_use_case),
):
    hoy = date.today()
    return MarcasRangoSalida(
        periodos=use_case.ejecutar_rango(anio or hoy.year, mes or hoy.month, cantidad)
    )


@router.post("/api/eventos", response_model=EventoSalida, status_code=status.HTTP_201_CREATED)
async def crear_evento(
    cuerpo: EventoEntrada,
    usuario: Usuario = Depends(obtener_usuario_actual),
    use_case: CrearEventoUseCase = Depends(crear_crear_evento_use_case),
    repositorio_asignaturas: RepositorioAsignaturas = Depends(obtener_repositorio_asignaturas),
    destinatarios_use_case: ObtenerDestinatariosAvisoUseCase = Depends(
        crear_obtener_destinatarios_aviso_use_case
    ),
):
    try:
        evento = use_case.ejecutar(
            CrearEventoCommand(
                codigo=cuerpo.codigo,
                tipo=cuerpo.tipo,
                fecha=cuerpo.fecha,
                hora=cuerpo.hora,
                lugar=cuerpo.lugar,
                solicitante_rol=usuario.rol,
                solicitante_email=usuario.email,
            )
        )
    except EstadoNoValido as error:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(error)})

    invalidar_cache_marcas()
    asignatura = next(
        (item for item in repositorio_asignaturas.obtener_todas() if item.codigo == evento.codigo),
        None,
    )
    salida = _evento_salida(evento, asignatura)
    destinatarios = destinatarios_use_case.ejecutar(
        salida.codigo, gestor.emails_conectados()
    )
    await gestor.difundir(
        {
            "tipo": "evento_nuevo",
            "id": salida.id,
            "codigo": salida.codigo,
            "tipo_evento": salida.tipo.value,
            "fecha": salida.fecha.isoformat(),
            "hora": salida.hora,
            "lugar": salida.lugar,
            "nombre": salida.nombre,
            "nombre_ingles": salida.nombre_ingles,
        },
        destinatarios,
    )
    return salida


@router.put("/api/eventos/{evento_id}", response_model=EventoSalida)
async def actualizar_evento(
    evento_id: str,
    cuerpo: EventoEntrada,
    usuario: Usuario = Depends(obtener_usuario_actual),
    use_case: ActualizarEventoUseCase = Depends(crear_actualizar_evento_use_case),
    repositorio_asignaturas: RepositorioAsignaturas = Depends(obtener_repositorio_asignaturas),
    destinatarios_use_case: ObtenerDestinatariosAvisoUseCase = Depends(
        crear_obtener_destinatarios_aviso_use_case
    ),
):
    try:
        evento = use_case.ejecutar(
            ActualizarEventoCommand(
                evento_id=evento_id,
                codigo=cuerpo.codigo,
                tipo=cuerpo.tipo,
                fecha=cuerpo.fecha,
                hora=cuerpo.hora,
                lugar=cuerpo.lugar,
                solicitante_rol=usuario.rol,
                solicitante_email=usuario.email,
            )
        )
    except EstadoNoValido as error:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(error)})

    invalidar_cache_marcas()
    asignatura = next(
        (item for item in repositorio_asignaturas.obtener_todas() if item.codigo == evento.codigo),
        None,
    )
    salida = _evento_salida(evento, asignatura)
    destinatarios = destinatarios_use_case.ejecutar(salida.codigo, gestor.emails_conectados())
    await gestor.difundir(
        {
            "tipo": "evento_actualizado",
            "id": salida.id,
            "codigo": salida.codigo,
            "tipo_evento": salida.tipo.value,
            "fecha": salida.fecha.isoformat(),
            "hora": salida.hora,
            "lugar": salida.lugar,
            "nombre": salida.nombre,
            "nombre_ingles": salida.nombre_ingles,
        },
        destinatarios,
    )
    return salida


@router.delete("/api/eventos/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_evento(
    evento_id: str,
    usuario: Usuario = Depends(obtener_usuario_actual),
    use_case: EliminarEventoUseCase = Depends(crear_eliminar_evento_use_case),
    destinatarios_use_case: ObtenerDestinatariosAvisoUseCase = Depends(
        crear_obtener_destinatarios_aviso_use_case
    ),
):
    try:
        existente = use_case.ejecutar(
            EliminarEventoCommand(
                evento_id=evento_id,
                solicitante_rol=usuario.rol,
                solicitante_email=usuario.email,
            )
        )
    except EstadoNoValido as error:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(error)})

    invalidar_cache_marcas()
    destinatarios = destinatarios_use_case.ejecutar(existente.codigo, gestor.emails_conectados())
    await gestor.difundir(
        {
            "tipo": "evento_eliminado",
            "id": evento_id,
            "codigo": existente.codigo,
            "tipo_evento": existente.tipo.value,
            "fecha": existente.fecha.isoformat(),
            "hora": existente.hora,
        },
        destinatarios,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _evento_salida(evento, asignatura) -> EventoSalida:
    return EventoSalida(
        id=identidad_evento(evento),
        fecha=evento.fecha,
        codigo=evento.codigo,
        tipo=evento.tipo,
        hora=evento.hora,
        lugar=evento.lugar,
        nombre=asignatura.nombre if asignatura else evento.codigo,
        nombre_ingles=asignatura.nombre_ingles if asignatura else evento.codigo,
    )
