from fastapi import APIRouter, Depends, status

from Servidor.ApiRest.ApiRestDependencies.auth_dependencies import obtener_administrador, obtener_usuario_actual
from Servidor.ApiRest.ApiRestDependencies.usuario_dependencies import (
    crear_eliminar_usuario_use_case,
    crear_numero_usuarios_use_case,
    crear_obtener_usuarios_use_case,
    crear_usuario_activo_use_case,
)
from Servidor.ApiRest.ApiRestSchemas.numero_usuarios_salida import NumeroUsuariosSalida
from Servidor.ApiRest.ApiRestSchemas.usuario_activo_salida import UsuarioActivoSalida
from Servidor.ApiRest.ApiRestSchemas.usuario_salida import UsuarioSalida
from Servidor.Infraestructura.registro_actividad import registro_actividad
from Servidor.Dominio.DominioCommands.eliminar_usuario_command import EliminarUsuarioCommand
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioQueries.numero_usuarios_query import NumeroUsuariosQuery
from Servidor.Dominio.DominioQueries.obtener_usuarios_query import ObtenerUsuariosQuery
from Servidor.Dominio.DominioQueries.usuario_activo_query import UsuarioActivoQuery
from Servidor.Dominio.DominioUseCases.eliminar_usuario_use_case import EliminarUsuarioUseCase
from Servidor.Dominio.DominioUseCases.numero_usuarios_use_case import NumeroUsuariosUseCase
from Servidor.Dominio.DominioUseCases.obtener_usuarios_use_case import ObtenerUsuariosUseCase
from Servidor.Dominio.DominioUseCases.usuario_activo_use_case import UsuarioActivoUseCase

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
