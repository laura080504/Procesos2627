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
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas_memoria import RepositorioAsignaturasMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas_mongo import RepositorioAsignaturasMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos import RepositorioCursos
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos_memoria import RepositorioCursosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos_mongo import RepositorioCursosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos_memoria import RepositorioEventosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos_mongo import RepositorioEventosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas_memoria import RepositorioMatriculasMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas_mongo import RepositorioMatriculasMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios_memoria import RepositorioUsuariosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from Servidor.Dominio.DominioUseCases.asegurar_administrador_use_case import AsegurarAdministradorUseCase
from Servidor.Dominio.DominioUseCases.asegurar_catalogo_asignaturas_use_case import AsegurarCatalogoAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.asegurar_eventos_muestra_use_case import AsegurarEventosMuestraUseCase
from Servidor.Dominio.DominioUseCases.asegurar_matriculas_muestra_use_case import AsegurarMatriculasMuestraUseCase


def crear_repositorios(
    configuracion: Configuracion,
) -> tuple[
    RepositorioUsuarios,
    RepositorioSesiones,
    RepositorioRecuperaciones,
    RepositorioConfirmaciones,
    RepositorioCursos,
    RepositorioAsignaturas,
    RepositorioEventos,
    RepositorioMatriculas,
]:
    if configuracion.motor_datos == "memoria":
        return (
            RepositorioUsuariosMemoria(),
            RepositorioSesionesMemoria(),
            RepositorioRecuperacionesMemoria(),
            RepositorioConfirmacionesMemoria(),
            RepositorioCursosMemoria(),
            RepositorioAsignaturasMemoria(),
            RepositorioEventosMemoria(),
            RepositorioMatriculasMemoria(),
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
            RepositorioCursosMongo(base_datos),
            RepositorioAsignaturasMongo(base_datos),
            RepositorioEventosMongo(base_datos),
            RepositorioMatriculasMongo(base_datos),
        )
    raise ValueError(f"El motor de datos '{configuracion.motor_datos}' no existe. Usa memoria o mongo.")


_configuracion = obtener_configuracion()
(
    _repositorio_usuarios,
    _repositorio_sesiones,
    _repositorio_recuperaciones,
    _repositorio_confirmaciones,
    _repositorio_cursos,
    _repositorio_asignaturas,
    _repositorio_eventos,
    _repositorio_matriculas,
) = crear_repositorios(_configuracion)
_enviador_correo = EnviadorCorreoBrevo(
    _configuracion.brevo_api_clave,
    _configuracion.brevo_remitente,
    _configuracion.brevo_remitente_nombre,
)
if _configuracion.admin_email and _configuracion.admin_contrasena:
    AsegurarAdministradorUseCase(_repositorio_usuarios, obtener_hasher_contrasenas()).ejecutar(
        _configuracion.admin_email, _configuracion.admin_contrasena
    )
AsegurarCatalogoAsignaturasUseCase(_repositorio_cursos, _repositorio_asignaturas).ejecutar()
AsegurarEventosMuestraUseCase(_repositorio_eventos, _repositorio_asignaturas).ejecutar()
AsegurarMatriculasMuestraUseCase(
    _repositorio_usuarios, _repositorio_matriculas, obtener_hasher_contrasenas()
).ejecutar()
_base = getattr(_repositorio_asignaturas, "base_datos", None)
if _base is not None and "asignaturas" in _base.base.list_collection_names():
    _base.base.drop_collection("asignaturas")


def obtener_repositorio_usuarios() -> RepositorioUsuarios:
    return _repositorio_usuarios


def obtener_repositorio_sesiones() -> RepositorioSesiones:
    return _repositorio_sesiones


def obtener_repositorio_recuperaciones() -> RepositorioRecuperaciones:
    return _repositorio_recuperaciones


def obtener_repositorio_confirmaciones() -> RepositorioConfirmaciones:
    return _repositorio_confirmaciones


def obtener_repositorio_cursos() -> RepositorioCursos:
    return _repositorio_cursos


def obtener_repositorio_asignaturas() -> RepositorioAsignaturas:
    return _repositorio_asignaturas


def obtener_repositorio_eventos() -> RepositorioEventos:
    return _repositorio_eventos


def obtener_repositorio_matriculas() -> RepositorioMatriculas:
    return _repositorio_matriculas


def obtener_enviador_correo() -> EnviadorCorreo:
    return _enviador_correo
