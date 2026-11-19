from datetime import date
from pathlib import Path

from Servidor.Dominio.DominioServices.cuatrimestre_actual import cuatrimestre_actual
from Servidor.Dominio.DominioServices.parser_calendario_esiiab import parsear_calendario_html
from Servidor.Dominio.DominioServices.parser_ficha_esiiab import parsear_ficha_html

FIXTURE_FICHA = Path(__file__).parent / "fixtures" / "asignatura_esiiab_muestra.html"
FIXTURE_CAL = Path(__file__).parent / "fixtures" / "calendario_academico_esiiab_offline.html"


def prueba_noviembre_es_primer_cuatrimestre():
    calendario = parsear_calendario_html(FIXTURE_CAL.read_text(encoding="utf-8"))
    assert cuatrimestre_actual(date(2026, 11, 19), calendario) == 1
    assert cuatrimestre_actual(date(2027, 1, 20), calendario) == 1
    assert cuatrimestre_actual(date(2027, 1, 26), calendario) == 2
    assert cuatrimestre_actual(date(2027, 3, 10), calendario) == 2


def prueba_tutorias_separadas_por_cuatrimestre_y_filtro_actual():
    ficha = parsear_ficha_html(FIXTURE_FICHA.read_text(encoding="utf-8"))
    barba = next(profesor for profesor in ficha.profesores if "BARBA" in profesor.nombre)
    assert any("Martes: 11:15" in franja for franja in barba.tutorias_primer)
    assert any("Miércoles: 10:00" in franja or "Miercoles: 10:00" in franja for franja in barba.tutorias_segundo)
    assert "Martes: 11:15" not in " ".join(barba.tutorias_segundo)
    assert barba.tutorias_de(1) == barba.tutorias_primer
    assert barba.tutorias_de(2) == barba.tutorias_segundo
