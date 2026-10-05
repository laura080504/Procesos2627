from servidor.datos.repositories.repositorio_recuperaciones import RepositorioRecuperaciones
from servidor.datos.repositories.repositorio_recuperaciones_memoria import RepositorioRecuperacionesMemoria
from servidor.datos.repositories.repositorio_sesiones import RepositorioSesiones
from servidor.datos.repositories.repositorio_sesiones_memoria import RepositorioSesionesMemoria
from servidor.datos.repositories.repositorio_usuarios import RepositorioUsuarios
from servidor.datos.repositories.repositorio_usuarios_memoria import RepositorioUsuariosMemoria

_repositorio_usuarios = RepositorioUsuariosMemoria()
_repositorio_sesiones = RepositorioSesionesMemoria()
_repositorio_recuperaciones = RepositorioRecuperacionesMemoria()


def obtener_repositorio_usuarios() -> RepositorioUsuarios:
    return _repositorio_usuarios


def obtener_repositorio_sesiones() -> RepositorioSesiones:
    return _repositorio_sesiones


def obtener_repositorio_recuperaciones() -> RepositorioRecuperaciones:
    return _repositorio_recuperaciones
