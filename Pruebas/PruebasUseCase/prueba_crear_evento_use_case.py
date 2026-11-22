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


def _command(codigo, tipo, dia, hora="23:59", lugar=None, rol=Rol.PROFESOR, email=EMAIL_PROFESOR):
    return CrearEventoCommand(
        codigo=codigo,
        tipo=tipo,
        fecha=date(2026, 11, dia),
        hora=hora,
        lugar=lugar,
        solicitante_rol=rol,
        solicitante_email=email,
    )


def prueba_profesor_publica_entrega_con_fecha_de_finalizacion():
    eventos, asignaturas, docencia = _repos()
    creado = CrearEventoUseCase(eventos, asignaturas, docencia).ejecutar(
        _command("42300", TipoEvento.ENTREGA, 20)
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
    eventos, asignaturas, docencia = _repos()
    with pytest.raises(PermisoInsuficiente):
        CrearEventoUseCase(eventos, asignaturas, docencia).ejecutar(
            _command("42300", TipoEvento.EXAMEN, 21, hora="09:00", lugar="Aula 1", rol=Rol.USUARIO)
        )


def prueba_profesor_no_publica_en_asignatura_ajena():
    eventos, asignaturas, docencia = _repos()
    with pytest.raises(PermisoInsuficiente):
        CrearEventoUseCase(eventos, asignaturas, docencia).ejecutar(
            _command("42302", TipoEvento.ENTREGA, 21)
        )
    assert eventos.obtener_todos() == []


def prueba_profesor_sin_docencia_no_publica():
    eventos, asignaturas, docencia = _repos()
    docencia.reemplazar(EMAIL_PROFESOR, [])
    with pytest.raises(PermisoInsuficiente):
        CrearEventoUseCase(eventos, asignaturas, docencia).ejecutar(
            _command("42300", TipoEvento.ENTREGA, 21)
        )


def prueba_superadministrador_publica_en_cualquier_asignatura():
    eventos, asignaturas, docencia = _repos()
    creado = CrearEventoUseCase(eventos, asignaturas, docencia).ejecutar(
        _command(
            "42302",
            TipoEvento.ENTREGA,
            21,
            rol=Rol.SUPERADMINISTRADOR,
            email="secretaria@ejemplo.com",
        )
    )
    assert creado.codigo == "42302"


def prueba_rechaza_asignatura_inexistente():
    eventos, asignaturas, docencia = _repos()
    with pytest.raises(EstadoNoValido, match="No existe la asignatura"):
        CrearEventoUseCase(eventos, asignaturas, docencia).ejecutar(
            _command("99999", TipoEvento.ENTREGA, 22)
        )
