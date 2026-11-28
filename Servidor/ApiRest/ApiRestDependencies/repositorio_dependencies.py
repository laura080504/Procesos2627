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
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaciones_rol import RepositorioAsignacionesRol
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaciones_rol_memoria import (
    RepositorioAsignacionesRolMemoria,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaciones_rol_mongo import (
    RepositorioAsignacionesRolMongo,
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
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_avisos_secretaria import (
    RepositorioAvisosSecretaria,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_avisos_secretaria_memoria import (
    RepositorioAvisosSecretariaMemoria,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_avisos_secretaria_mongo import (
    RepositorioAvisosSecretariaMongo,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos_memoria import RepositorioEventosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos_mongo import RepositorioEventosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas_memoria import RepositorioMatriculasMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas_mongo import RepositorioMatriculasMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia import RepositorioDocencia
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia_memoria import RepositorioDocenciaMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia_mongo import RepositorioDocenciaMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_esiiab import RepositorioEsiiab
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_esiiab_memoria import RepositorioEsiiabMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_esiiab_mongo import RepositorioEsiiabMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios_memoria import RepositorioUsuariosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from Servidor.Dominio.DominioServices.docencia_muestra import (
    asegurar_docencia_muestra,
    asegurar_rol_profesor_gallud,
)
from Servidor.Dominio.DominioServices.horario_esiiab import configurar_proveedor_sesiones
from Servidor.Dominio.DominioUseCases.asegurar_administrador_use_case import AsegurarAdministradorUseCase
from Servidor.Dominio.DominioUseCases.asegurar_catalogo_asignaturas_use_case import AsegurarCatalogoAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.asegurar_avisos_secretaria_muestra_use_case import (
    AsegurarAvisosSecretariaMuestraUseCase,
)
from Servidor.Dominio.DominioUseCases.asegurar_eventos_muestra_use_case import AsegurarEventosMuestraUseCase
from Servidor.Dominio.DominioUseCases.asegurar_matriculas_muestra_use_case import AsegurarMatriculasMuestraUseCase
from Servidor.Dominio.DominioUseCases.asegurar_secretaria_use_case import AsegurarSecretariaUseCase
from Servidor.Infraestructura.cliente_horarios_esiiab import ClienteHorariosEsiiab
from Servidor.Infraestructura.sincronizador_esiiab import SincronizadorEsiiab


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
    RepositorioEsiiab,
    RepositorioDocencia,
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
            RepositorioEsiiabMemoria(),
            RepositorioDocenciaMemoria(),
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
            RepositorioEsiiabMongo(base_datos),
            RepositorioDocenciaMongo(base_datos),
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
    _repositorio_esiiab,
    _repositorio_docencia,
) = crear_repositorios(_configuracion)
if _configuracion.motor_datos == "mongo" and isinstance(_repositorio_usuarios, RepositorioUsuariosMongo):
    _repositorio_asignaciones_rol: RepositorioAsignacionesRol = RepositorioAsignacionesRolMongo(
        _repositorio_usuarios.base_datos
    )
else:
    _repositorio_asignaciones_rol = RepositorioAsignacionesRolMemoria()
if _configuracion.motor_datos == "mongo" and isinstance(_repositorio_usuarios, RepositorioUsuariosMongo):
    _repositorio_avisos_secretaria: RepositorioAvisosSecretaria = RepositorioAvisosSecretariaMongo(
        _repositorio_usuarios.base_datos
    )
else:
    _repositorio_avisos_secretaria = RepositorioAvisosSecretariaMemoria()
_enviador_correo = EnviadorCorreoBrevo(
    _configuracion.brevo_smtp_servidor,
    _configuracion.brevo_smtp_puerto,
    _configuracion.brevo_smtp_usuario,
    _configuracion.brevo_smtp_clave,
    _configuracion.brevo_remitente,
    _configuracion.brevo_remitente_nombre,
    _configuracion.brevo_api_clave,
)
_cliente_horarios_esiiab = ClienteHorariosEsiiab(
    url=_configuracion.horarios_esiiab_url,
    ttl_segundos=_configuracion.horarios_esiiab_ttl_segundos,
    vivo=_configuracion.horarios_esiiab_vivo,
)
_sincronizador_esiiab = SincronizadorEsiiab(
    _cliente_horarios_esiiab,
    _repositorio_esiiab,
    ttl_segundos=_configuracion.horarios_esiiab_ttl_segundos,
)
configurar_proveedor_sesiones(_sincronizador_esiiab.sesiones)
_sincronizador_esiiab.iniciar_en_segundo_plano()
if _configuracion.admin_email and _configuracion.admin_contrasena:
    # ADMIN_* = profesor (administrador académico), no secretaría.
    AsegurarAdministradorUseCase(_repositorio_usuarios, obtener_hasher_contrasenas()).ejecutar(
        _configuracion.admin_email, _configuracion.admin_contrasena
    )
if _configuracion.secretaria_email and _configuracion.secretaria_contrasena:
    AsegurarSecretariaUseCase(_repositorio_usuarios, obtener_hasher_contrasenas()).ejecutar(
        _configuracion.secretaria_email, _configuracion.secretaria_contrasena
    )
AsegurarCatalogoAsignaturasUseCase(_repositorio_cursos, _repositorio_asignaturas).ejecutar()
AsegurarEventosMuestraUseCase(_repositorio_eventos, _repositorio_asignaturas).ejecutar()
AsegurarAvisosSecretariaMuestraUseCase(_repositorio_avisos_secretaria).ejecutar()
AsegurarMatriculasMuestraUseCase(
    _repositorio_usuarios, _repositorio_matriculas, obtener_hasher_contrasenas()
).ejecutar()
asegurar_docencia_muestra(_repositorio_docencia)
asegurar_rol_profesor_gallud(_repositorio_usuarios)
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


def obtener_repositorio_asignaciones_rol() -> RepositorioAsignacionesRol:
    return _repositorio_asignaciones_rol


def obtener_repositorio_cursos() -> RepositorioCursos:
    return _repositorio_cursos


def obtener_repositorio_asignaturas() -> RepositorioAsignaturas:
    return _repositorio_asignaturas


def obtener_repositorio_eventos() -> RepositorioEventos:
    return _repositorio_eventos


def obtener_repositorio_avisos_secretaria() -> RepositorioAvisosSecretaria:
    return _repositorio_avisos_secretaria


def obtener_repositorio_matriculas() -> RepositorioMatriculas:
    return _repositorio_matriculas


def obtener_repositorio_docencia() -> RepositorioDocencia:
    return _repositorio_docencia


def obtener_enviador_correo() -> EnviadorCorreo:
    return _enviador_correo


def obtener_cliente_horarios_esiiab() -> SincronizadorEsiiab:
    return _sincronizador_esiiab


def obtener_repositorio_esiiab() -> RepositorioEsiiab:
    return _repositorio_esiiab
