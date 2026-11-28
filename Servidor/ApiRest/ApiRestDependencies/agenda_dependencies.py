from fastapi import Depends

from Servidor.ApiRest.ApiRestDependencies.repositorio_dependencies import (
    obtener_cliente_horarios_esiiab,
    obtener_repositorio_asignaturas,
    obtener_repositorio_docencia,
    obtener_repositorio_eventos,
    obtener_repositorio_matriculas,
)
from Servidor.Dominio.DominioUseCases.crear_evento_use_case import CrearEventoUseCase
from Servidor.Dominio.DominioUseCases.guardar_expediente_use_case import GuardarExpedienteUseCase
from Servidor.Dominio.DominioUseCases.guardar_matricula_use_case import GuardarMatriculaUseCase
from Servidor.Dominio.DominioUseCases.listar_asignaturas_use_case import ListarAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.obtener_destinatarios_aviso_use_case import (
    ObtenerDestinatariosAvisoUseCase,
)
from Servidor.Dominio.DominioUseCases.obtener_expediente_use_case import ObtenerExpedienteUseCase
from Servidor.Dominio.DominioUseCases.obtener_marcas_calendario_use_case import ObtenerMarcasCalendarioUseCase
from Servidor.Dominio.DominioUseCases.obtener_matricula_use_case import ObtenerMatriculaUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia import RepositorioDocencia
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas

# Singletons: las cachés en proceso solo sirven si sobreviven entre peticiones.
_listar_asignaturas = ListarAsignaturasUseCase(obtener_repositorio_asignaturas())
_obtener_marcas = ObtenerMarcasCalendarioUseCase(
    obtener_repositorio_eventos(),
    obtener_repositorio_asignaturas(),
    obtener_cliente_horarios_esiiab(),
)
_obtener_matricula = ObtenerMatriculaUseCase(
    obtener_repositorio_matriculas(),
    obtener_repositorio_asignaturas(),
    obtener_cliente_horarios_esiiab(),
    obtener_repositorio_docencia(),
)
_guardar_matricula = GuardarMatriculaUseCase(
    obtener_repositorio_matriculas(),
    obtener_repositorio_asignaturas(),
    _obtener_matricula,
)
_obtener_expediente = ObtenerExpedienteUseCase(
    obtener_repositorio_matriculas(),
    obtener_repositorio_asignaturas(),
)
_guardar_expediente = GuardarExpedienteUseCase(
    obtener_repositorio_matriculas(),
    obtener_repositorio_asignaturas(),
    _obtener_expediente,
    _obtener_matricula.invalidar_cache,
)


def crear_listar_asignaturas_use_case() -> ListarAsignaturasUseCase:
    return _listar_asignaturas


def crear_obtener_marcas_calendario_use_case() -> ObtenerMarcasCalendarioUseCase:
    return _obtener_marcas


def crear_obtener_matricula_use_case() -> ObtenerMatriculaUseCase:
    return _obtener_matricula


def crear_guardar_matricula_use_case() -> GuardarMatriculaUseCase:
    return _guardar_matricula


def crear_obtener_expediente_use_case() -> ObtenerExpedienteUseCase:
    return _obtener_expediente


def crear_guardar_expediente_use_case() -> GuardarExpedienteUseCase:
    return _guardar_expediente


def crear_crear_evento_use_case(
    repositorio_eventos: RepositorioEventos = Depends(obtener_repositorio_eventos),
    repositorio_asignaturas: RepositorioAsignaturas = Depends(obtener_repositorio_asignaturas),
    repositorio_docencia: RepositorioDocencia = Depends(obtener_repositorio_docencia),
) -> CrearEventoUseCase:
    return CrearEventoUseCase(
        repositorio_eventos,
        repositorio_asignaturas,
        repositorio_docencia,
    )


def crear_obtener_destinatarios_aviso_use_case(
    repositorio_matriculas: RepositorioMatriculas = Depends(obtener_repositorio_matriculas),
) -> ObtenerDestinatariosAvisoUseCase:
    return ObtenerDestinatariosAvisoUseCase(repositorio_matriculas)


def invalidar_cache_marcas() -> None:
    _obtener_marcas.invalidar_cache()
