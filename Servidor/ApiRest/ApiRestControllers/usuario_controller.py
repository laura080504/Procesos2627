from fastapi import APIRouter, Depends, Request, status

from Servidor.ApiRest.ApiRestDependencies.auth_dependencies import (
    obtener_gestor,
    obtener_superadministrador,
    obtener_usuario_actual,
)
from Servidor.ApiRest.ApiRestDependencies.configuracion_dependencies import obtener_configuracion
from Servidor.configuracion import Configuracion
from Servidor.ApiRest.ApiRestDependencies.agenda_dependencies import (
    crear_guardar_matricula_use_case,
    crear_obtener_matricula_use_case,
)
from Servidor.ApiRest.ApiRestDependencies.usuario_dependencies import (
    crear_asignar_administrador_use_case,
    crear_asignar_delegado_use_case,
    crear_confirmar_asignacion_rol_use_case,
    crear_editar_alumno_secretaria_use_case,
    crear_editar_datos_use_case,
    crear_eliminar_usuario_use_case,
    crear_numero_usuarios_use_case,
    crear_obtener_usuarios_use_case,
    crear_solicitar_asignacion_rol_use_case,
    crear_usuario_activo_use_case,
)
from Servidor.ApiRest.ApiRestSchemas.editar_datos_entrada import EditarDatosEntrada
from Servidor.ApiRest.ApiRestSchemas.matricula_entrada import MatriculaEntrada
from Servidor.ApiRest.ApiRestSchemas.matricula_salida import MatriculaSalida
from Servidor.ApiRest.ApiRestSchemas.numero_usuarios_salida import NumeroUsuariosSalida
from Servidor.ApiRest.ApiRestSchemas.confirmar_entrada import ConfirmarEntrada
from Servidor.ApiRest.ApiRestSchemas.usuario_activo_salida import UsuarioActivoSalida
from Servidor.ApiRest.ApiRestSchemas.usuario_listado_salida import UsuarioListadoSalida
from Servidor.ApiRest.ApiRestSchemas.usuario_salida import UsuarioSalida
from Servidor.Infraestructura.registro_actividad import registro_actividad
from Servidor.Dominio.DominioCommands.asignar_administrador_command import AsignarAdministradorCommand
from Servidor.Dominio.DominioCommands.editar_datos_command import EditarDatosCommand
from Servidor.Dominio.DominioCommands.eliminar_usuario_command import EliminarUsuarioCommand
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioQueries.numero_usuarios_query import NumeroUsuariosQuery
from Servidor.Dominio.DominioQueries.obtener_usuarios_query import ObtenerUsuariosQuery
from Servidor.Dominio.DominioQueries.usuario_activo_query import UsuarioActivoQuery
from Servidor.Dominio.DominioUseCases.asignar_administrador_use_case import AsignarAdministradorUseCase
from Servidor.Dominio.DominioUseCases.asignar_delegado_use_case import AsignarDelegadoUseCase
from Servidor.Dominio.DominioUseCases.confirmar_asignacion_rol_use_case import ConfirmarAsignacionRolUseCase
from Servidor.Dominio.DominioUseCases.editar_alumno_secretaria_use_case import EditarAlumnoSecretariaUseCase
from Servidor.Dominio.DominioUseCases.editar_datos_use_case import EditarDatosUseCase
from Servidor.Dominio.DominioUseCases.eliminar_usuario_use_case import EliminarUsuarioUseCase
from Servidor.Dominio.DominioUseCases.guardar_matricula_use_case import (
    AsignaturaMatriculaEntrada,
    GuardarMatriculaUseCase,
)
from Servidor.Dominio.DominioUseCases.numero_usuarios_use_case import NumeroUsuariosUseCase
from Servidor.Dominio.DominioUseCases.obtener_matricula_use_case import ObtenerMatriculaUseCase
from Servidor.Dominio.DominioUseCases.obtener_usuarios_use_case import ObtenerUsuariosUseCase
from Servidor.Dominio.DominioUseCases.solicitar_asignacion_rol_use_case import SolicitarAsignacionRolUseCase
from Servidor.Dominio.DominioUseCases.usuario_activo_use_case import UsuarioActivoUseCase
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


def _url_base(request: Request, configuracion: Configuracion) -> str:
    if configuracion.url_publica:
        return configuracion.url_publica
    return str(request.base_url).rstrip("/")


def _usuario_salida(usuario: Usuario) -> UsuarioSalida:
    return UsuarioSalida(
        email=usuario.email,
        nick=usuario.nick,
        rol=usuario.rol,
        estado=usuario.estado,
        delegado_curso=usuario.delegado_curso,
    )


@router.get("", response_model=list[UsuarioListadoSalida])
def obtener_usuarios(
    usuario: Usuario = Depends(obtener_gestor),
    use_case: ObtenerUsuariosUseCase = Depends(crear_obtener_usuarios_use_case),
):
    return [
        UsuarioListadoSalida(
            email=resultado.usuario.email,
            nick=resultado.usuario.nick,
            rol=resultado.usuario.rol,
            estado=resultado.usuario.estado,
            delegado_curso=resultado.usuario.delegado_curso,
            asignaturas=resultado.asignaturas,
            media=resultado.media,
            curso=resultado.curso,
        )
        for resultado in use_case.ejecutar(
            ObtenerUsuariosQuery(
                solicitante_rol=usuario.rol,
                solicitante_email=usuario.email,
            )
        )
    ]


@router.patch("/me", response_model=UsuarioSalida)
def editar_datos(
    datos: EditarDatosEntrada,
    solicitante: Usuario = Depends(obtener_usuario_actual),
    use_case: EditarDatosUseCase = Depends(crear_editar_datos_use_case),
):
    usuario = use_case.ejecutar(
        EditarDatosCommand(
            solicitante_email=solicitante.email,
            email=datos.email,
            nick=datos.nick,
            contrasena=datos.contrasena,
        )
    )
    registro_actividad.edicion(solicitante.email, usuario.email)
    return _usuario_salida(usuario)


@router.get("/numero", response_model=NumeroUsuariosSalida)
def numero_usuarios(
    _: Usuario = Depends(obtener_gestor),
    use_case: NumeroUsuariosUseCase = Depends(crear_numero_usuarios_use_case),
):
    return NumeroUsuariosSalida(numero=use_case.ejecutar(NumeroUsuariosQuery()))


@router.post("/confirmar-rol", response_model=UsuarioSalida)
def confirmar_asignacion_rol(
    datos: ConfirmarEntrada,
    use_case: ConfirmarAsignacionRolUseCase = Depends(crear_confirmar_asignacion_rol_use_case),
):
    usuario = use_case.ejecutar(datos.token)
    return _usuario_salida(usuario)


@router.post("/{email}/asignar-rol", status_code=status.HTTP_204_NO_CONTENT)
def solicitar_asignacion_rol(
    email: str,
    request: Request,
    solicitante: Usuario = Depends(obtener_superadministrador),
    use_case: SolicitarAsignacionRolUseCase = Depends(crear_solicitar_asignacion_rol_use_case),
    configuracion: Configuracion = Depends(obtener_configuracion),
):
    use_case.ejecutar(
        email,
        solicitante.rol,
        _url_base(request, configuracion),
        Rol.PROFESOR,
        solicitante.email,
    )
    registro_actividad.asignacion_rol(solicitante.email, email.strip().lower())


@router.post("/{email}/delegado", response_model=UsuarioSalida)
def asignar_delegado(
    email: str,
    solicitante: Usuario = Depends(obtener_superadministrador),
    use_case: AsignarDelegadoUseCase = Depends(crear_asignar_delegado_use_case),
):
    try:
        usuario = use_case.ejecutar(email, solicitante.rol, activar=True)
    except EstadoNoValido as error:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(error)})
    return _usuario_salida(usuario)


@router.delete("/{email}/delegado", response_model=UsuarioSalida)
def quitar_delegado(
    email: str,
    solicitante: Usuario = Depends(obtener_superadministrador),
    use_case: AsignarDelegadoUseCase = Depends(crear_asignar_delegado_use_case),
):
    usuario = use_case.ejecutar(email, solicitante.rol, activar=False)
    return _usuario_salida(usuario)


@router.get("/{email}/matricula", response_model=MatriculaSalida)
def matricula_de_alumno(
    email: str,
    _: Usuario = Depends(obtener_superadministrador),
    use_case: ObtenerMatriculaUseCase = Depends(crear_obtener_matricula_use_case),
):
    return use_case.ejecutar(email.strip().lower(), "")


@router.put("/{email}/matricula", response_model=MatriculaSalida)
def guardar_matricula_de_alumno(
    email: str,
    cuerpo: MatriculaEntrada,
    _: Usuario = Depends(obtener_superadministrador),
    use_case: GuardarMatriculaUseCase = Depends(crear_guardar_matricula_use_case),
):
    try:
        return use_case.ejecutar(
            email.strip().lower(),
            [
                AsignaturaMatriculaEntrada(asignatura.codigo, asignatura.grupo)
                for asignatura in cuerpo.asignaturas
            ],
        )
    except EstadoNoValido as error:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(error)})


@router.patch("/{email}", response_model=UsuarioSalida)
def editar_alumno_por_secretaria(
    email: str,
    datos: EditarDatosEntrada,
    solicitante: Usuario = Depends(obtener_superadministrador),
    use_case: EditarAlumnoSecretariaUseCase = Depends(crear_editar_alumno_secretaria_use_case),
):
    usuario = use_case.ejecutar(email, datos.email, datos.nick, solicitante.rol)
    registro_actividad.edicion(solicitante.email, usuario.email)
    return _usuario_salida(usuario)


@router.post("/{email}/profesor", response_model=UsuarioSalida)
def asignar_profesor(
    email: str,
    solicitante: Usuario = Depends(obtener_superadministrador),
    use_case: AsignarAdministradorUseCase = Depends(crear_asignar_administrador_use_case),
):
    # Compatibilidad: el flujo preferido es /asignar-rol + confirmación por correo.
    usuario = use_case.ejecutar(
        AsignarAdministradorCommand(
            email=email,
            solicitante_email=solicitante.email,
            solicitante_rol=solicitante.rol,
            rol_destino=Rol.PROFESOR,
        )
    )
    registro_actividad.asignacion_rol(solicitante.email, usuario.email)
    return _usuario_salida(usuario)


@router.get("/{email}/activo", response_model=UsuarioActivoSalida)
def usuario_activo(
    email: str,
    _: Usuario = Depends(obtener_gestor),
    use_case: UsuarioActivoUseCase = Depends(crear_usuario_activo_use_case),
):
    return UsuarioActivoSalida(email=email, activo=use_case.ejecutar(UsuarioActivoQuery(email=email)))


@router.delete("/{email}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    email: str,
    solicitante: Usuario = Depends(obtener_usuario_actual),
    use_case: EliminarUsuarioUseCase = Depends(crear_eliminar_usuario_use_case),
):
    use_case.ejecutar(
        EliminarUsuarioCommand(
            email=email, solicitante_email=solicitante.email, solicitante_rol=solicitante.rol
        )
    )
    registro_actividad.eliminacion(solicitante.email, email.strip().lower())
