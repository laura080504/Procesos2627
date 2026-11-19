from pathlib import Path

from Servidor.Dominio.DominioServices.parser_ficha_esiiab import FichaEsiiab, ProfesorEsiiab, parsear_ficha_html
from Servidor.Infraestructura.cliente_horarios_esiiab import ClienteHorariosEsiiab
from Servidor.Infraestructura.sincronizador_esiiab import _ficha_obsoleta

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
    assert any("Martes" in franja for franja in barba.tutorias_primer)
    assert any("10:00" in franja for franja in barba.tutorias_segundo)
    assert not any("11:15" in franja for franja in barba.tutorias_segundo)
    assert barba.url.endswith("/personal/barba-sanchez-virginia/")
    assert not _ficha_obsoleta(ficha)


def prueba_ficha_con_un_profesor_igual_en_ambos_cuatris_sigue_siendo_valida():
    """Sahori en SD: mismas horas 1.º/2.º no debe invalidar la ficha entera."""
    ficha = FichaEsiiab(
        "42322",
        "Sistemas Distribuidos",
        "https://esiiab.uclm.es/asignatura/sistemas-distribuidos/",
        (
            ProfesorEsiiab("CAMBRONERO", "", (), ()),
            ProfesorEsiiab("SAHORI", "", ("Jueves: 8:15 - 11:30",), ("Jueves: 8:15 - 11:30",)),
            ProfesorEsiiab("MUÑOZ", "", ("Martes: 17:00 - 18:00",), ()),
        ),
    )
    assert not _ficha_obsoleta(ficha)


def prueba_ficha_con_bloque_duplicado_completo_sigue_obsoleta():
    franjas = ("Lunes: 10:00 - 12:00",)
    ficha = FichaEsiiab(
        "99999",
        "Asignatura Fake",
        "",
        (ProfesorEsiiab("UNO", "", franjas, franjas), ProfesorEsiiab("DOS", "", franjas, franjas)),
    )
    assert _ficha_obsoleta(ficha)


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
