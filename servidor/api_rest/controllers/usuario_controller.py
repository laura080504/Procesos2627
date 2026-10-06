from fastapi import APIRouter, Depends, status

from servidor.api_rest.dependencies.auth_dependencies import obtener_administrador, obtener_usuario_actual
from servidor.api_rest.dependencies.usuario_dependencies import (
    crear_eliminar_usuario_use_case,
    crear_numero_usuarios_use_case,
    crear_obtener_usuarios_use_case,
    crear_usuario_activo_use_case,
)
from servidor.api_rest.schemas.numero_usuarios_salida import NumeroUsuariosSalida
from servidor.api_rest.schemas.usuario_activo_salida import UsuarioActivoSalida
from servidor.api_rest.schemas.usuario_salida import UsuarioSalida
from servidor.infraestructura.registro_actividad import registro_actividad
from servidor.dominio.commands.eliminar_usuario_command import EliminarUsuarioCommand
from servidor.dominio.entities.usuario import Usuario
from servidor.dominio.queries.numero_usuarios_query import NumeroUsuariosQuery
from servidor.dominio.queries.obtener_usuarios_query import ObtenerUsuariosQuery
from servidor.dominio.queries.usuario_activo_query import UsuarioActivoQuery
from servidor.dominio.use_cases.eliminar_usuario_use_case import EliminarUsuarioUseCase
from servidor.dominio.use_cases.numero_usuarios_use_case import NumeroUsuariosUseCase
from servidor.dominio.use_cases.obtener_usuarios_use_case import ObtenerUsuariosUseCase
from servidor.dominio.use_cases.usuario_activo_use_case import UsuarioActivoUseCase

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioSalida])
def obtener_usuarios(
    _: Usuario = Depends(obtener_administrador),
    use_case: ObtenerUsuariosUseCase = Depends(crear_obtener_usuarios_use_case),
):
    return use_case.ejecutar(ObtenerUsuariosQuery())


@router.get("/numero", response_model=NumeroUsuariosSalida)
def numero_usuarios(
    _: Usuario = Depends(obtener_administrador),
    use_case: NumeroUsuariosUseCase = Depends(crear_numero_usuarios_use_case),
):
    return NumeroUsuariosSalida(numero=use_case.ejecutar(NumeroUsuariosQuery()))


@router.get("/{email}/activo", response_model=UsuarioActivoSalida)
def usuario_activo(
    email: str,
    _: Usuario = Depends(obtener_administrador),
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
