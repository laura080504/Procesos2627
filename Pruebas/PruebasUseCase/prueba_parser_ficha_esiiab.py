from pathlib import Path

from Servidor.Dominio.DominioServices.parser_ficha_esiiab import parsear_ficha_html
from Servidor.Infraestructura.cliente_horarios_esiiab import ClienteHorariosEsiiab

FIXTURE = Path(__file__).parent / "fixtures" / "asignatura_esiiab_muestra.html"
HORARIOS = Path(__file__).parent / "fixtures" / "horarios_esiiab_offline.html"


def prueba_el_parser_extrae_profesores_y_tutorias():
    ficha = parsear_ficha_html(
        FIXTURE.read_text(encoding="utf-8"),
        url="https://esiiab.uclm.es/asignatura/fundamentos-de-gestion-empresarial/",
    )
    assert ficha.codigo == "42304"
    nombres = {profesor.nombre for profesor in ficha.profesores}
    assert "BARBA SANCHEZ, VIRGINIA" in nombres
    assert "LÓPEZ HERNÁNDEZ, ALBERTO" in nombres
    barba = next(profesor for profesor in ficha.profesores if "BARBA" in profesor.nombre)
    assert any("Martes" in franja for franja in barba.tutorias)
    assert barba.url.endswith("/personal/barba-sanchez-virginia/")


def prueba_el_cliente_descarga_fichas_de_asignaturas_matriculadas():
    horarios = HORARIOS.read_text(encoding="utf-8")
    ficha_html = FIXTURE.read_text(encoding="utf-8")

    def descargar(url: str) -> str:
        if "horarios" in url:
            return horarios
        return ficha_html

    cliente = ClienteHorariosEsiiab(vivo=True, descargar=descargar, ttl_segundos=60)
    fichas = cliente.fichas_de([("42304", "Fundamentos de Gestión Empresarial")])
    assert "42304" in fichas
    assert len(fichas["42304"].profesores) >= 2
