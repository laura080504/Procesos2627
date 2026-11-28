from datetime import date

import pytest

from Servidor.Dominio.DominioCommands.actualizar_evento_command import ActualizarEventoCommand
from Servidor.Dominio.DominioCommands.crear_evento_command import CrearEventoCommand
from Servidor.Dominio.DominioCommands.eliminar_evento_command import EliminarEventoCommand
from Servidor.Dominio.DominioEntities.evento import identidad_evento
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioUseCases.actualizar_evento_use_case import ActualizarEventoUseCase
from Servidor.Dominio.DominioUseCases.asegurar_catalogo_asignaturas_use_case import AsegurarCatalogoAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.crear_evento_use_case import CrearEventoUseCase
from Servidor.Dominio.DominioUseCases.eliminar_evento_use_case import EliminarEventoUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas_memoria import RepositorioAsignaturasMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos_memoria import RepositorioCursosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia_memoria import RepositorioDocenciaMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos_memoria import RepositorioEventosMemoria

EMAIL_PROFESOR = "profesor@ejemplo.com"


def _repos():
    cursos = RepositorioCursosMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    eventos = RepositorioEventosMemoria()
    docencia = RepositorioDocenciaMemoria()
    docencia.reemplazar(EMAIL_PROFESOR, ["42300"])
    AsegurarCatalogoAsignaturasUseCase(cursos, asignaturas).ejecutar()
    return eventos, asignaturas, docencia


def _crear(eventos, asignaturas, docencia):
    return CrearEventoUseCase(eventos, asignaturas, docencia).ejecutar(
        CrearEventoCommand(
            codigo="42300",
            tipo=TipoEvento.EXAMEN,
            fecha=date(2026, 11, 30),
            hora="09:00",
            lugar="Aula 1.4",
            solicitante_rol=Rol.PROFESOR,
            solicitante_email=EMAIL_PROFESOR,
        )
    )


def prueba_profesor_actualiza_su_evento():
    eventos, asignaturas, docencia = _repos()
    creado = _crear(eventos, asignaturas, docencia)
    actualizado = ActualizarEventoUseCase(eventos, asignaturas, docencia).ejecutar(
        ActualizarEventoCommand(
            evento_id=identidad_evento(creado),
            codigo="42300",
            tipo=TipoEvento.ENTREGA,
            fecha=date(2026, 12, 1),
            hora="23:59",
            lugar=None,
            solicitante_rol=Rol.PROFESOR,
            solicitante_email=EMAIL_PROFESOR,
        )
    )
    assert identidad_evento(actualizado) == identidad_evento(creado)
    assert actualizado.tipo == TipoEvento.ENTREGA
    assert actualizado.fecha == date(2026, 12, 1)
    assert actualizado.hora == "23:59"
    assert eventos.obtener_por_id(identidad_evento(creado)) == actualizado


def prueba_profesor_elimina_su_evento():
    eventos, asignaturas, docencia = _repos()
    creado = _crear(eventos, asignaturas, docencia)
    EliminarEventoUseCase(eventos, docencia).ejecutar(
        EliminarEventoCommand(
            evento_id=identidad_evento(creado),
            solicitante_rol=Rol.PROFESOR,
            solicitante_email=EMAIL_PROFESOR,
        )
    )
    assert eventos.obtener_todos() == []


def prueba_profesor_no_elimina_evento_ajeno():
    eventos, asignaturas, docencia = _repos()
    creado = _crear(eventos, asignaturas, docencia)
    docencia.reemplazar(EMAIL_PROFESOR, ["42302"])
    with pytest.raises(PermisoInsuficiente):
        EliminarEventoUseCase(eventos, docencia).ejecutar(
            EliminarEventoCommand(
                evento_id=identidad_evento(creado),
                solicitante_rol=Rol.PROFESOR,
                solicitante_email=EMAIL_PROFESOR,
            )
        )
