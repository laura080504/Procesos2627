from Servidor.ApiRest.ApiRestDependencies.configuracion_dependencies import (
    obtener_configuracion,
    obtener_hasher_contrasenas,
)
from Servidor.configuracion import Configuracion
from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo
from Servidor.Infraestructura.enviador_correo import EnviadorCorreo
from Servidor.Infraestructura.enviador_correo_brevo import EnviadorCorreoBrevo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_confirmaciones import RepositorioConfirmaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_confirmaciones_memoria import (
    RepositorioConfirmacionesMemoria,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_confirmaciones_mongo import (
    RepositorioConfirmacionesMongo,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones import RepositorioRecuperaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones_memoria import RepositorioRecuperacionesMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones_mongo import RepositorioRecuperacionesMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones_memoria import RepositorioSesionesMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones_mongo import RepositorioSesionesMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios_memoria import RepositorioUsuariosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from Servidor.Dominio.DominioUseCases.asegurar_administrador_use_case import AsegurarAdministradorUseCase


def crear_repositorios(
    configuracion: Configuracion,
) -> tuple[RepositorioUsuarios, RepositorioSesiones, RepositorioRecuperaciones, RepositorioConfirmaciones]:
    if configuracion.motor_datos == "memoria":
        return (
            RepositorioUsuariosMemoria(),
            RepositorioSesionesMemoria(),
            RepositorioRecuperacionesMemoria(),
            RepositorioConfirmacionesMemoria(),
        )
    if configuracion.motor_datos == "mongo":
        base_datos = BaseDatosMongo(
            configuracion.mongo_uri or "",
            configuracion.mongo_db,
            usuario=configuracion.mongo_usuario,
            contrasena=configuracion.mongo_contrasena,
        )
        return (
            RepositorioUsuariosMongo(base_datos),
            RepositorioSesionesMongo(base_datos),
            RepositorioRecuperacionesMongo(base_datos),
            RepositorioConfirmacionesMongo(base_datos),
        )
    raise ValueError(f"El motor de datos '{configuracion.motor_datos}' no existe. Usa memoria o mongo.")


_configuracion = obtener_configuracion()
_repositorio_usuarios, _repositorio_sesiones, _repositorio_recuperaciones, _repositorio_confirmaciones = (
    crear_repositorios(_configuracion)
)
_enviador_correo = EnviadorCorreoBrevo(
    _configuracion.brevo_api_clave,
    _configuracion.brevo_remitente,
    _configuracion.brevo_remitente_nombre,
)
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


def obtener_repositorio_confirmaciones() -> RepositorioConfirmaciones:
    return _repositorio_confirmaciones


def obtener_enviador_correo() -> EnviadorCorreo:
    return _enviador_correo
