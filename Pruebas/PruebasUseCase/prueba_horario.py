from Servidor.Dominio.DominioServices.horario_asignatura import franjas_de
from Servidor.Dominio.DominioServices.matriculas_muestra import CODIGOS_LAURA, EMAIL_LAURA, GRUPOS_LAURA
from Servidor.Dominio.DominioUseCases.asegurar_catalogo_asignaturas_use_case import AsegurarCatalogoAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.obtener_matricula_use_case import ObtenerMatriculaUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas_memoria import RepositorioAsignaturasMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos_memoria import RepositorioCursosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas_memoria import RepositorioMatriculasMemoria


def _catalogo():
    cursos = RepositorioCursosMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    AsegurarCatalogoAsignaturasUseCase(cursos, asignaturas).ejecutar()
    return asignaturas


def prueba_el_horario_reproduce_el_grupo_a_de_la_esiiab():
    asignaturas = _catalogo().obtener_todas()
    franjas = franjas_de(asignaturas, {asignatura.codigo: "A" for asignatura in asignaturas})
    calculo = [franja for franja in franjas if franja.codigo == "42300"]
    assert any(
        franja.dia == 4 and franja.inicio == "08:15" and franja.fin == "09:45" and franja.tipo == "teoria"
        for franja in calculo
    )
    programacion = [franja for franja in franjas if franja.codigo == "42302"]
    assert any(franja.dia == 4 and franja.inicio == "11:35" and franja.tipo == "practicas" for franja in programacion)
    for franja in franjas:
        assert 0 <= franja.dia <= 4
        assert franja.inicio < franja.fin
        assert franja.tipo in ("teoria", "practicas")
        # Horarios únicos (sin A/B en ESIIAB) no inventan etiqueta de grupo.
        if franja.grupo:
            assert franja.grupo == "A"


def prueba_aspectos_grupo_11_solo_segunda_franja():
    from pathlib import Path

    from Servidor.Dominio.DominioServices.horario_esiiab import configurar_proveedor_sesiones
    from Servidor.Dominio.DominioServices.parser_horarios_esiiab import parsear_horarios_html

    offline = Path(__file__).parent / "fixtures" / "horarios_esiiab_offline.html"
    horario = parsear_horarios_html(offline.read_text(encoding="utf-8"))
    configurar_proveedor_sesiones(lambda: horario.sesiones)
    try:
        api = next(a for a in _catalogo().obtener_todas() if a.codigo == "42325")
        del_11 = franjas_de([api], {"42325": "11"})
        del_10 = franjas_de([api], {"42325": "10"})
        assert del_11 and all(franja.grupo == "B" for franja in del_11)
        assert all(franja.inicio == "13:05" and franja.fin == "14:35" for franja in del_11)
        assert del_10 and all(franja.grupo == "A" for franja in del_10)
        assert all(franja.inicio == "11:35" and franja.fin == "13:05" for franja in del_10)
    finally:
        from Servidor.ApiRest.ApiRestDependencies.repositorio_dependencies import (
            obtener_cliente_horarios_esiiab,
        )

        configurar_proveedor_sesiones(obtener_cliente_horarios_esiiab().sesiones)


def prueba_el_horario_cruza_matricula_con_grupo_esiiab():
    asignaturas = _catalogo()
    matriculas = RepositorioMatriculasMemoria()
    codigos = ["42314", "42322", "42324"]
    grupos = {"42314": "A", "42322": "B", "42324": "B"}
    matriculas.reemplazar_alumno("alumno@ejemplo.com", codigos, grupos)
    resultado = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar("alumno@ejemplo.com")
    assert {franja.codigo for franja in resultado.horario} == set(codigos)
    for franja in resultado.horario:
        assert franja.grupo == grupos[franja.codigo]
        assert franja.cuatrimestre == 1
    distribuidos = [franja for franja in resultado.horario if franja.codigo == "42322"]
    assert distribuidos and all(franja.grupo == "B" for franja in distribuidos)
    software = [franja for franja in resultado.horario if franja.codigo == "42314"]
    assert software and all(franja.grupo == "A" for franja in software)
    assert any(franja.dia == 3 and franja.inicio == "11:35" and franja.fin == "13:05" for franja in software)


def prueba_laura_guarda_grupos_oficiales_de_campus():
    asignaturas = _catalogo()
    matriculas = RepositorioMatriculasMemoria()
    matriculas.reemplazar_alumno(EMAIL_LAURA, list(CODIGOS_LAURA), dict(GRUPOS_LAURA))
    resultado = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar(EMAIL_LAURA)
    assert {asignatura.codigo for asignatura in resultado.asignaturas} == set(CODIGOS_LAURA)
    assert {asignatura.codigo: asignatura.grupo for asignatura in resultado.asignaturas} == dict(GRUPOS_LAURA)


def prueba_laura_ve_horario_traduciendo_grupos_de_campus():
    asignaturas = _catalogo()
    matriculas = RepositorioMatriculasMemoria()
    matriculas.reemplazar_alumno(EMAIL_LAURA, list(CODIGOS_LAURA), dict(GRUPOS_LAURA))
    resultado = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar(EMAIL_LAURA)
    # El API trae ambos cuatrimestres; el cliente filtra por la semana vista.
    del_primero = {franja.codigo for franja in resultado.horario if franja.cuatrimestre == 1}
    del_segundo = {franja.codigo for franja in resultado.horario if franja.cuatrimestre == 2}
    assert {"42322", "42324", "42330", "42332", "42333"} <= del_primero
    assert "42305" not in del_primero
    assert "42326" in del_segundo or "42305" in del_segundo
    assert "42366" not in del_segundo  # Auditoría es 1.er cuatri (ESIIAB O1 - 1 Semestre)
    assert {asignatura.codigo for asignatura in resultado.asignaturas} == set(CODIGOS_LAURA)
    distribuidos = [franja for franja in resultado.horario if franja.codigo == "42322"]
    assert distribuidos and all(franja.grupo == "B" for franja in distribuidos)
    procesos = [franja for franja in resultado.horario if franja.codigo == "42330"]
    assert procesos and all(franja.grupo == "ING. SOFTWARE" for franja in procesos)
