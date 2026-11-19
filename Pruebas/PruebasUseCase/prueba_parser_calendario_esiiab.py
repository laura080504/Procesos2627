from pathlib import Path

from Servidor.Dominio.DominioServices.parser_calendario_esiiab import parsear_calendario_html

FIXTURE = Path(__file__).parent / "fixtures" / "calendario_academico_esiiab_offline.html"


def prueba_parsea_festivos_cuatrimestres_y_examenes():
    calendario = parsear_calendario_html(FIXTURE.read_text(encoding="utf-8"))
    assert calendario.curso.startswith("2026")
    tipos = {fecha.tipo for fecha in calendario.fechas}
    assert "festivo" in tipos
    assert "vacaciones" in tipos
    assert "inicio_cuatrimestre" in tipos
    assert "fin_cuatrimestre" in tipos
    assert "inicio_examenes_ordinarios" in tipos
    assert "inicio_examenes_extraordinarios" in tipos
    navidad = next(fecha for fecha in calendario.fechas if fecha.titulo == "Navidad")
    assert navidad.inicio.isoformat() == "2026-12-24"
    assert navidad.fin.isoformat() == "2027-01-07"
