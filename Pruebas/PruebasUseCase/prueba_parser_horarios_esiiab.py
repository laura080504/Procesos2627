from pathlib import Path

from Servidor.Dominio.DominioServices.horario_esiiab import configurar_proveedor_sesiones, sesiones_de
from Servidor.Dominio.DominioServices.parser_horarios_esiiab import parsear_horarios_html
from Servidor.Infraestructura.cliente_horarios_esiiab import ClienteHorariosEsiiab

FIXTURE = Path(__file__).parent / "fixtures" / "horarios_esiiab_muestra.html"
OFFLINE = Path(__file__).parent / "fixtures" / "horarios_esiiab_offline.html"


def prueba_el_parser_extrae_franjas_del_grupo_a():
    horario = parsear_horarios_html(FIXTURE.read_text(encoding="utf-8"))
    calculo = horario.sesiones["calculo y metodos numericos"]
    assert (4, "08:15", "09:45", "teoria", "AULA 1.11", "A") in calculo
    assert (2, "09:45", "11:15", "teoria", "AULA 1.11", "A") in calculo
    programacion = horario.sesiones["fundamentos de programacion i"]
    assert any(
        franja[0] == 4 and franja[1] == "11:35" and franja[3] == "practicas" and franja[5] == "A"
        for franja in programacion
    )


def prueba_el_parser_guarda_urls_de_ficha():
    horario = parsear_horarios_html(OFFLINE.read_text(encoding="utf-8"))
    url = horario.urls["fundamentos de gestion empresarial"]
    assert url.rstrip("/").endswith("/asignatura/fundamentos-de-gestion-empresarial")


def prueba_el_parser_incluye_todos_los_grupos_e_intensificaciones():
    horario = parsear_horarios_html(OFFLINE.read_text(encoding="utf-8"))
    assert {"A", "B", "C", "I"}.issubset(set(horario.grupos))
    assert any("COMPUTAC" in grupo or "SOFTWARE" in grupo or grupo.startswith("O") for grupo in horario.grupos)
    calculo = horario.sesiones["calculo y metodos numericos"]
    grupos_calculo = {franja[5] for franja in calculo}
    assert {"A", "B", "C", "I"}.issubset(grupos_calculo)
    # Grupo B de 1º: Cálculo el lunes a las 8:15
    assert any(franja[5] == "B" and franja[0] == 0 and franja[1] == "08:15" for franja in calculo)


def prueba_el_parser_incluye_aspectos_profesionales_sin_cabecera_grupo():
    horario = parsear_horarios_html(OFFLINE.read_text(encoding="utf-8"))
    aspectos = horario.sesiones["aspectos profesionales de la informatica"]
    assert aspectos
    assert any(franja[1] == "11:35" and franja[2] == "13:05" for franja in aspectos)
    assert any(franja[1] == "13:05" and franja[2] == "14:35" for franja in aspectos)


def prueba_el_cliente_refresca_desde_html_y_usa_cache():
    html = FIXTURE.read_text(encoding="utf-8")
    descargas = {"n": 0}

    def descargar(_url: str) -> str:
        descargas["n"] += 1
        return html

    cliente = ClienteHorariosEsiiab(ttl_segundos=60, vivo=True, descargar=descargar)
    primero = cliente.sesiones()
    segundo = cliente.sesiones()
    assert descargas["n"] == 1
    assert primero is segundo
    assert "calculo y metodos numericos" in primero


def prueba_el_cliente_offline_usa_el_html_embebido():
    cliente = ClienteHorariosEsiiab(vivo=False, html_offline=OFFLINE)
    mapa = cliente.sesiones()
    assert "calculo y metodos numericos" in mapa
    assert "A" in cliente.grupos()


def prueba_sesiones_de_usa_el_proveedor_vivo():
    from Servidor.ApiRest.ApiRestDependencies.repositorio_dependencies import obtener_cliente_horarios_esiiab

    html = FIXTURE.read_text(encoding="utf-8")
    cliente = ClienteHorariosEsiiab(vivo=True, descargar=lambda _url: html)
    configurar_proveedor_sesiones(cliente.sesiones)
    try:
        franjas = sesiones_de("Fundamentos de Programación I")
        assert any(franja[0] == 4 and franja[1] == "11:35" and franja[3] == "practicas" for franja in franjas)
    finally:
        configurar_proveedor_sesiones(obtener_cliente_horarios_esiiab().sesiones)
