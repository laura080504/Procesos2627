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
        assert franja.grupo == "A"


def prueba_el_horario_cruza_matricula_con_grupo_esiiab():
    asignaturas = _catalogo()
    matriculas = RepositorioMatriculasMemoria()
    # Solo 1º cuatrimestre: en noviembre el horario filtra por periodo vigente.
    codigos = ["42314", "42322", "42324"]
    grupos = {"42314": "A", "42322": "B", "42324": "B"}
    matriculas.reemplazar_alumno("alumno@ejemplo.com", codigos, grupos)
    resultado = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar("alumno@ejemplo.com")
    assert {franja.codigo for franja in resultado.horario} == set(codigos)
    for franja in resultado.horario:
        assert franja.grupo == grupos[franja.codigo]
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
    por_codigo = {franja.codigo for franja in resultado.horario}
    # En noviembre (1º cuatri) solo salen asignaturas de ese cuatrimestre.
    assert {"42322", "42324", "42330", "42332", "42333"} <= por_codigo
    assert "42305" not in por_codigo
    assert "42326" not in por_codigo
    assert "42366" not in por_codigo
    # La lista de matrícula sigue completa.
    assert {asignatura.codigo for asignatura in resultado.asignaturas} == set(CODIGOS_LAURA)
    distribuidos = [franja for franja in resultado.horario if franja.codigo == "42322"]
    assert distribuidos and all(franja.grupo == "B" for franja in distribuidos)
    procesos = [franja for franja in resultado.horario if franja.codigo == "42330"]
    assert procesos and all(franja.grupo == "ING. SOFTWARE" for franja in procesos)
