from datetime import date

from Servidor.Dominio.DominioEntities.evento import Evento
from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento
from Servidor.Dominio.DominioQueries.obtener_marcas_calendario_query import ObtenerMarcasCalendarioQuery
from Servidor.Dominio.DominioUseCases.asegurar_catalogo_asignaturas_use_case import AsegurarCatalogoAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.asegurar_eventos_muestra_use_case import AsegurarEventosMuestraUseCase
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


def prueba_asegurar_eventos_limpia_la_semilla_ficticia():
    eventos, asignaturas = _repos()
    eventos.reemplazar(
        [
            Evento(date(2026, 10, 11), "42300", TipoEvento.EXAMEN, "09:00", "Aula Multiusos"),
            Evento(date(2026, 11, 19), "42304", TipoEvento.ENTREGA, "23:59", None),
        ]
    )
    AsegurarEventosMuestraUseCase(eventos, asignaturas).ejecutar()
    assert eventos.obtener_todos() == []


def prueba_octubre_sin_semilla_no_inventa_estrellas():
    eventos, asignaturas = _repos()
    AsegurarEventosMuestraUseCase(eventos, asignaturas).ejecutar()
    marcas = ObtenerMarcasCalendarioUseCase(eventos, asignaturas).ejecutar(ObtenerMarcasCalendarioQuery(2026, 10))
    estrellas = [
        simbolo
        for marca in marcas
        for simbolo in marca.simbolos
        if simbolo.tipo == "estrella"
    ]
    assert estrellas == []


def prueba_avisos_reales_del_profesor_siguen_marcando():
    eventos, asignaturas = _repos()
    eventos.guardar(Evento(date(2026, 12, 15), "42302", TipoEvento.ENTREGA, "23:59", None))
    marcas = ObtenerMarcasCalendarioUseCase(eventos, asignaturas).ejecutar(ObtenerMarcasCalendarioQuery(2026, 12))
    del_15 = next(marca for marca in marcas if marca.dia == 15)
    assert any(simbolo.tipo == "punto" and simbolo.codigo == "42302" for simbolo in del_15.simbolos)
