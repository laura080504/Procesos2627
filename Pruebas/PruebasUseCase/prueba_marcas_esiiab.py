from pathlib import Path

from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento
from Servidor.Dominio.DominioEntities.evento import Evento
from Servidor.Dominio.DominioQueries.obtener_marcas_calendario_query import ObtenerMarcasCalendarioQuery
from Servidor.Dominio.DominioServices.marcas_calendario import marcas_del_mes
from Servidor.Dominio.DominioServices.parser_calendario_esiiab import parsear_calendario_html
from Servidor.Dominio.DominioServices.parser_examenes_esiiab import parsear_examenes_html
from Servidor.Dominio.DominioUseCases.asegurar_catalogo_asignaturas_use_case import AsegurarCatalogoAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.obtener_marcas_calendario_use_case import ObtenerMarcasCalendarioUseCase
from Servidor.Infraestructura.cliente_horarios_esiiab import ClienteHorariosEsiiab
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas_memoria import (
    RepositorioAsignaturasMemoria,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos_memoria import RepositorioCursosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_esiiab_memoria import RepositorioEsiiabMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos_memoria import RepositorioEventosMemoria
from Servidor.Infraestructura.sincronizador_esiiab import SincronizadorEsiiab
from datetime import date

FIXTURES = Path(__file__).parent / "fixtures"


def _catalogo():
    cursos = RepositorioCursosMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    AsegurarCatalogoAsignaturasUseCase(cursos, asignaturas).ejecutar()
    return {asignatura.codigo: asignatura for asignatura in asignaturas.obtener_todas()}


def prueba_marcas_mezclan_festivo_oficial_y_examen_de_matricula():
    catalogo = _catalogo()
    calendario = parsear_calendario_html(
        (FIXTURES / "calendario_academico_esiiab_offline.html").read_text(encoding="utf-8")
    )
    examenes = parsear_examenes_html((FIXTURES / "examenes_esiiab_offline.html").read_text(encoding="utf-8"))
    eventos = [
        Evento(date(2027, 1, 20), "42300", TipoEvento.EXAMEN, "08:00", "fake"),
        Evento(date(2027, 1, 15), "42300", TipoEvento.ENTREGA, "23:59"),
    ]
    marcas = marcas_del_mes(eventos, catalogo, 2027, 1, examenes=examenes, calendario=calendario)
    por_dia = {marca.dia: marca.simbolos for marca in marcas}
    assert any(simbolo.tipo == "vacaciones" for simbolo in por_dia[1])
    assert any(simbolo.tipo == "festivo" for simbolo in por_dia[25])
    estrellas = [simbolo for simbolo in por_dia[20] if simbolo.tipo == "estrella" and simbolo.codigo == "42300"]
    assert len(estrellas) == 1
    assert estrellas[0].hora == "09:30"
    assert "ESII" in (estrellas[0].lugar or "")


def prueba_use_case_carga_calendario_y_examenes_offline():
    cursos = RepositorioCursosMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    eventos = RepositorioEventosMemoria()
    AsegurarCatalogoAsignaturasUseCase(cursos, asignaturas).ejecutar()
    sync = SincronizadorEsiiab(ClienteHorariosEsiiab(vivo=False), RepositorioEsiiabMemoria())
    marcas = ObtenerMarcasCalendarioUseCase(eventos, asignaturas, sync).ejecutar(
        ObtenerMarcasCalendarioQuery(2026, 10)
    )
    tipos = {simbolo.tipo for marca in marcas for simbolo in marca.simbolos}
    assert "festivo" in tipos


def prueba_extraordinarios_llegan_hasta_el_2_de_julio():
    calendario = parsear_calendario_html(
        (FIXTURES / "calendario_academico_esiiab_offline.html").read_text(encoding="utf-8")
    )
    marcas = marcas_del_mes([], _catalogo(), 2027, 7, calendario=calendario)
    por_dia = {marca.dia: [simbolo.tipo for simbolo in marca.simbolos] for marca in marcas}
    assert por_dia[1] == ["semana_examenes"]
    assert por_dia[2] == ["semana_examenes"]
    assert 3 not in por_dia
