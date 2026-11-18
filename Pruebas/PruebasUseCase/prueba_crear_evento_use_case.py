from datetime import date

import pytest

from Servidor.Dominio.DominioCommands.crear_evento_command import CrearEventoCommand
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento
from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioQueries.obtener_marcas_calendario_query import ObtenerMarcasCalendarioQuery
from Servidor.Dominio.DominioUseCases.asegurar_catalogo_asignaturas_use_case import AsegurarCatalogoAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.crear_evento_use_case import CrearEventoUseCase
from Servidor.Dominio.DominioUseCases.obtener_marcas_calendario_use_case import ObtenerMarcasCalendarioUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas_memoria import RepositorioAsignaturasMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos_memoria import RepositorioCursosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos_memoria import RepositorioEventosMemoria


def _repos():
    cursos = RepositorioCursosMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    eventos = RepositorioEventosMemoria()
    AsegurarCatalogoAsignaturasUseCase(cursos, asignaturas).ejecutar()
    return eventos, asignaturas


def prueba_profesor_publica_entrega_con_fecha_de_finalizacion():
    eventos, asignaturas = _repos()
    creado = CrearEventoUseCase(eventos, asignaturas).ejecutar(
        CrearEventoCommand(
            codigo="42300",
            tipo=TipoEvento.ENTREGA,
            fecha=date(2026, 11, 20),
            hora="23:59",
            lugar=None,
            solicitante_rol=Rol.PROFESOR,
        )
    )
    assert creado.fecha == date(2026, 11, 20)
    assert creado.hora == "23:59"
    marcas = ObtenerMarcasCalendarioUseCase(eventos, asignaturas).ejecutar(
        ObtenerMarcasCalendarioQuery(2026, 11)
    )
    del_20 = next(marca for marca in marcas if marca.dia == 20)
    simbolo = next(item for item in del_20.simbolos if item.codigo == "42300")
    assert simbolo.tipo == "punto"
    assert simbolo.fecha == "2026-11-20"
    assert simbolo.hora == "23:59"


def prueba_alumno_no_puede_crear_evento():
    eventos, asignaturas = _repos()
    with pytest.raises(PermisoInsuficiente):
        CrearEventoUseCase(eventos, asignaturas).ejecutar(
            CrearEventoCommand(
                codigo="42300",
                tipo=TipoEvento.EXAMEN,
                fecha=date(2026, 11, 21),
                hora="09:00",
                lugar="Aula 1",
                solicitante_rol=Rol.USUARIO,
            )
        )


def prueba_rechaza_asignatura_inexistente():
    eventos, asignaturas = _repos()
    with pytest.raises(EstadoNoValido, match="No existe la asignatura"):
        CrearEventoUseCase(eventos, asignaturas).ejecutar(
            CrearEventoCommand(
                codigo="99999",
                tipo=TipoEvento.ENTREGA,
                fecha=date(2026, 11, 22),
                hora="23:59",
                lugar=None,
                solicitante_rol=Rol.PROFESOR,
            )
        )
