from pydantic import Field

from Servidor.ApiRest.ApiRestSchemas.usuario_salida import UsuarioSalida


class UsuarioListadoSalida(UsuarioSalida):
    asignaturas: list[str] = Field(default_factory=list)
