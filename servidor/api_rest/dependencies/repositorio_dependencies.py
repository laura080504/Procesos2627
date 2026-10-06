from servidor.api_rest.dependencies.configuracion_dependencies import obtener_configuracion
from servidor.configuracion import Configuracion
from servidor.infraestructura.base_datos_sqlite import BaseDatosSqlite
from servidor.infraestructura.repositories.repositorio_recuperaciones import RepositorioRecuperaciones
from servidor.infraestructura.repositories.repositorio_recuperaciones_memoria import RepositorioRecuperacionesMemoria
from servidor.infraestructura.repositories.repositorio_recuperaciones_sqlite import RepositorioRecuperacionesSqlite
from servidor.infraestructura.repositories.repositorio_sesiones import RepositorioSesiones
from servidor.infraestructura.repositories.repositorio_sesiones_memoria import RepositorioSesionesMemoria
from servidor.infraestructura.repositories.repositorio_sesiones_sqlite import RepositorioSesionesSqlite
from servidor.infraestructura.repositories.repositorio_usuarios import RepositorioUsuarios
from servidor.infraestructura.repositories.repositorio_usuarios_memoria import RepositorioUsuariosMemoria
from servidor.infraestructura.repositories.repositorio_usuarios_sqlite import RepositorioUsuariosSqlite


def crear_repositorios(
    configuracion: Configuracion,
) -> tuple[RepositorioUsuarios, RepositorioSesiones, RepositorioRecuperaciones]:
    if configuracion.motor_datos == "memoria":
        return (
            RepositorioUsuariosMemoria(),
            RepositorioSesionesMemoria(),
            RepositorioRecuperacionesMemoria(),
        )
    if configuracion.motor_datos == "sqlite":
        base_datos = BaseDatosSqlite(configuracion.ruta_datos)
        return (
            RepositorioUsuariosSqlite(base_datos),
            RepositorioSesionesSqlite(base_datos),
            RepositorioRecuperacionesSqlite(base_datos),
        )
    raise ValueError(f"El motor de datos '{configuracion.motor_datos}' no existe. Usa sqlite o memoria.")


_configuracion = obtener_configuracion()
_repositorio_usuarios, _repositorio_sesiones, _repositorio_recuperaciones = crear_repositorios(_configuracion)


def obtener_repositorio_usuarios() -> RepositorioUsuarios:
    return _repositorio_usuarios


def obtener_repositorio_sesiones() -> RepositorioSesiones:
    return _repositorio_sesiones


def obtener_repositorio_recuperaciones() -> RepositorioRecuperaciones:
    return _repositorio_recuperaciones
