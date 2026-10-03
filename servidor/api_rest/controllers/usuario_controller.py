from fastapi import APIRouter, Depends, status

from servidor.api_rest.dependencies import (
    crear_agregar_usuario_use_case,
    crear_eliminar_usuario_use_case,
    crear_numero_usuarios_use_case,
    crear_obtener_usuarios_use_case,
    crear_usuario_activo_use_case,
)
from servidor.api_rest.schemas import (
    NumeroUsuariosSalida,
    UsuarioActivoSalida,
    UsuarioEntrada,
    UsuarioSalida,
)
from servidor.logica.commands import AgregarUsuarioCommand, EliminarUsuarioCommand
from servidor.logica.queries import NumeroUsuariosQuery, ObtenerUsuariosQuery, UsuarioActivoQuery
from servidor.logica.use_cases import (
    AgregarUsuarioUseCase,
    EliminarUsuarioUseCase,
    NumeroUsuariosUseCase,
    ObtenerUsuariosUseCase,
    UsuarioActivoUseCase,
)

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


@router.post("", response_model=UsuarioSalida, status_code=status.HTTP_201_CREATED)
def agregar_usuario(
    datos: UsuarioEntrada,
    use_case: AgregarUsuarioUseCase = Depends(crear_agregar_usuario_use_case),
):
    return use_case.ejecutar(AgregarUsuarioCommand(nick=datos.nick))


@router.get("", response_model=list[UsuarioSalida])
def obtener_usuarios(use_case: ObtenerUsuariosUseCase = Depends(crear_obtener_usuarios_use_case)):
    return use_case.ejecutar(ObtenerUsuariosQuery())


@router.get("/numero", response_model=NumeroUsuariosSalida)
def numero_usuarios(use_case: NumeroUsuariosUseCase = Depends(crear_numero_usuarios_use_case)):
    return NumeroUsuariosSalida(numero=use_case.ejecutar(NumeroUsuariosQuery()))


@router.get("/{nick}/activo", response_model=UsuarioActivoSalida)
def usuario_activo(nick: str, use_case: UsuarioActivoUseCase = Depends(crear_usuario_activo_use_case)):
    return UsuarioActivoSalida(nick=nick, activo=use_case.ejecutar(UsuarioActivoQuery(nick=nick)))


@router.delete("/{nick}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(nick: str, use_case: EliminarUsuarioUseCase = Depends(crear_eliminar_usuario_use_case)):
    use_case.ejecutar(EliminarUsuarioCommand(nick=nick))
