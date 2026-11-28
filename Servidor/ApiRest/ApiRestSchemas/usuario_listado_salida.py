from pydantic import Field

from Servidor.ApiRest.ApiRestSchemas.usuario_salida import UsuarioSalida
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura


class UsuarioListadoSalida(UsuarioSalida):
    asignaturas: list[str] = Field(default_factory=list)
    media: float | None = None
    curso: CursoAsignatura | None = None
