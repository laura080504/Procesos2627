from Servidor.ApiRest.ApiRestDependencies.configuracion_dependencies import (
    obtener_configuracion,
    obtener_hasher_contrasenas,
)
from Servidor.configuracion import Configuracion
from Servidor.Infraestructura.base_datos_sqlite import BaseDatosSqlite
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones import RepositorioRecuperaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones_memoria import RepositorioRecuperacionesMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones_sqlite import RepositorioRecuperacionesSqlite
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones_memoria import RepositorioSesionesMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones_sqlite import RepositorioSesionesSqlite
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios_memoria import RepositorioUsuariosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios_sqlite import RepositorioUsuariosSqlite
from Servidor.Dominio.DominioUseCases.asegurar_administrador_use_case import AsegurarAdministradorUseCase


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
if _configuracion.admin_email and _configuracion.admin_contrasena:
    AsegurarAdministradorUseCase(_repositorio_usuarios, obtener_hasher_contrasenas()).ejecutar(
        _configuracion.admin_email, _configuracion.admin_contrasena
    )


def obtener_repositorio_usuarios() -> RepositorioUsuarios:
    return _repositorio_usuarios


def obtener_repositorio_sesiones() -> RepositorioSesiones:
    return _repositorio_sesiones


def obtener_repositorio_recuperaciones() -> RepositorioRecuperaciones:
    return _repositorio_recuperaciones
