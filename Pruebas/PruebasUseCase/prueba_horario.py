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


def prueba_el_horario_de_laura_cruza_matricula_con_su_grupo():
    asignaturas = _catalogo()
    matriculas = RepositorioMatriculasMemoria()
    matriculas.reemplazar_alumno(EMAIL_LAURA, list(CODIGOS_LAURA), dict(GRUPOS_LAURA))
    resultado = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar(EMAIL_LAURA)
    assert {franja.codigo for franja in resultado.horario} == set(CODIGOS_LAURA)
    for franja in resultado.horario:
        assert franja.grupo == GRUPOS_LAURA[franja.codigo]
    algebra = [franja for franja in resultado.horario if franja.codigo == "42305"]
    assert algebra and all(franja.grupo == "B" for franja in algebra)
    assert any(franja.dia == 4 and franja.inicio == "08:15" and franja.tipo == "teoria" for franja in algebra)
    software = [franja for franja in resultado.horario if franja.codigo == "42314"]
    assert software and all(franja.grupo == "A" for franja in software)
    assert any(franja.dia == 3 and franja.inicio == "11:35" and franja.fin == "13:05" for franja in software)
