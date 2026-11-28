from fastapi import Depends

from Servidor.ApiRest.ApiRestDependencies.configuracion_dependencies import obtener_hasher_contrasenas
from datetime import timedelta

from Servidor.ApiRest.ApiRestDependencies.repositorio_dependencies import (
    obtener_cliente_horarios_esiiab,
    obtener_enviador_correo,
    obtener_repositorio_asignaciones_rol,
    obtener_repositorio_asignaturas,
    obtener_repositorio_docencia,
    obtener_repositorio_matriculas,
    obtener_repositorio_recuperaciones,
    obtener_repositorio_sesiones,
    obtener_repositorio_usuarios,
)
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas
from Servidor.Dominio.DominioUseCases.asignar_administrador_use_case import AsignarAdministradorUseCase
from Servidor.Dominio.DominioUseCases.asignar_delegado_use_case import AsignarDelegadoUseCase
from Servidor.Dominio.DominioUseCases.confirmar_asignacion_rol_use_case import ConfirmarAsignacionRolUseCase
from Servidor.Dominio.DominioUseCases.editar_datos_use_case import EditarDatosUseCase
from Servidor.Dominio.DominioUseCases.eliminar_usuario_use_case import EliminarUsuarioUseCase
from Servidor.Dominio.DominioUseCases.numero_usuarios_use_case import NumeroUsuariosUseCase
from Servidor.Dominio.DominioUseCases.obtener_horario_alumno_use_case import ObtenerHorarioAlumnoUseCase
from Servidor.Dominio.DominioUseCases.obtener_matricula_use_case import ObtenerMatriculaUseCase
from Servidor.Dominio.DominioUseCases.obtener_usuarios_use_case import ObtenerUsuariosUseCase
from Servidor.Dominio.DominioUseCases.solicitar_asignacion_rol_use_case import SolicitarAsignacionRolUseCase
from Servidor.Dominio.DominioUseCases.usuario_activo_use_case import UsuarioActivoUseCase
from Servidor.Infraestructura.enviador_correo import EnviadorCorreo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaciones_rol import (
    RepositorioAsignacionesRol,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia import RepositorioDocencia
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones import RepositorioRecuperaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios


def crear_obtener_usuarios_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_matriculas: RepositorioMatriculas = Depends(obtener_repositorio_matriculas),
    repositorio_docencia: RepositorioDocencia = Depends(obtener_repositorio_docencia),
    repositorio_asignaturas: RepositorioAsignaturas = Depends(obtener_repositorio_asignaturas),
) -> ObtenerUsuariosUseCase:
    return ObtenerUsuariosUseCase(
        repositorio_usuarios,
        repositorio_matriculas,
        repositorio_docencia,
        repositorio_asignaturas,
    )


def crear_obtener_horario_alumno_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_matriculas: RepositorioMatriculas = Depends(obtener_repositorio_matriculas),
    repositorio_docencia: RepositorioDocencia = Depends(obtener_repositorio_docencia),
    repositorio_asignaturas: RepositorioAsignaturas = Depends(obtener_repositorio_asignaturas),
) -> ObtenerHorarioAlumnoUseCase:
    # Repos inyectados (los de la petición, también en pruebas). El cliente ESIIAB
    # solo enriquece fichas; las franjas salen del catálogo y de la matrícula.
    obtener_matricula = ObtenerMatriculaUseCase(
        repositorio_matriculas,
        repositorio_asignaturas,
        obtener_cliente_horarios_esiiab(),
        repositorio_docencia,
    )
    return ObtenerHorarioAlumnoUseCase(
        repositorio_usuarios,
        repositorio_matriculas,
        repositorio_docencia,
        repositorio_asignaturas,
        obtener_matricula,
    )


def crear_usuario_activo_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
) -> UsuarioActivoUseCase:
    return UsuarioActivoUseCase(repositorio_usuarios)


def crear_numero_usuarios_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
) -> NumeroUsuariosUseCase:
    return NumeroUsuariosUseCase(repositorio_usuarios)


def crear_editar_datos_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_sesiones: RepositorioSesiones = Depends(obtener_repositorio_sesiones),
    repositorio_recuperaciones: RepositorioRecuperaciones = Depends(obtener_repositorio_recuperaciones),
    hasher: HasherContrasenas = Depends(obtener_hasher_contrasenas),
) -> EditarDatosUseCase:
    return EditarDatosUseCase(
        repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones, hasher
    )


def crear_asignar_administrador_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
) -> AsignarAdministradorUseCase:
    return AsignarAdministradorUseCase(repositorio_usuarios)


def crear_eliminar_usuario_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_sesiones: RepositorioSesiones = Depends(obtener_repositorio_sesiones),
    repositorio_recuperaciones: RepositorioRecuperaciones = Depends(obtener_repositorio_recuperaciones),
) -> EliminarUsuarioUseCase:
    return EliminarUsuarioUseCase(repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones)


def crear_solicitar_asignacion_rol_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_asignaciones: RepositorioAsignacionesRol = Depends(obtener_repositorio_asignaciones_rol),
    enviador: EnviadorCorreo = Depends(obtener_enviador_correo),
) -> SolicitarAsignacionRolUseCase:
    return SolicitarAsignacionRolUseCase(
        repositorio_usuarios, repositorio_asignaciones, enviador, timedelta(hours=24)
    )


def crear_confirmar_asignacion_rol_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_asignaciones: RepositorioAsignacionesRol = Depends(obtener_repositorio_asignaciones_rol),
) -> ConfirmarAsignacionRolUseCase:
    return ConfirmarAsignacionRolUseCase(repositorio_usuarios, repositorio_asignaciones)


def crear_asignar_delegado_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_matriculas: RepositorioMatriculas = Depends(obtener_repositorio_matriculas),
    repositorio_asignaturas: RepositorioAsignaturas = Depends(obtener_repositorio_asignaturas),
) -> AsignarDelegadoUseCase:
    return AsignarDelegadoUseCase(repositorio_usuarios, repositorio_matriculas, repositorio_asignaturas)
