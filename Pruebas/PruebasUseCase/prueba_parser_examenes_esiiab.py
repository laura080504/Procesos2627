from pathlib import Path

from Servidor.Dominio.DominioServices.parser_examenes_esiiab import parsear_examenes_html

FIXTURE = Path(__file__).parent / "fixtures" / "examenes_esiiab_offline.html"


def prueba_parsea_ordinaria_y_extraordinaria_con_aula():
    examenes = parsear_examenes_html(FIXTURE.read_text(encoding="utf-8"))
    assert len(examenes.examenes) >= 10
    calculo = next(
        examen
        for examen in examenes.examenes
        if examen.nombre == "Cálculo y Métodos Numéricos" and examen.convocatoria == "ordinaria"
    )
    assert calculo.fecha.isoformat() == "2027-01-20"
    assert calculo.hora == "09:30"
    assert "1.1" in calculo.aulas
    assert any(examen.convocatoria == "extraordinaria" for examen in examenes.examenes)
