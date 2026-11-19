from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioServices.curso_alumno import curso_del_alumno
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
    return asignaturas.obtener_todas()


def _por_codigo(catalogo):
    return {asignatura.codigo: asignatura for asignatura in catalogo}


def prueba_mas_de_la_mitad_de_sus_asignaturas_asigna_ese_curso():
    catalogo = _catalogo()
    por_codigo = _por_codigo(catalogo)
    primero = [por_codigo[codigo] for codigo in ("42300", "42301", "42302", "42303", "42304", "42305", "42306")]
    propias = primero + [por_codigo["42310"]]
    assert curso_del_alumno(propias) == CursoAsignatura.PRIMERO


def prueba_la_mitad_exacta_no_asigna_curso():
    catalogo = _catalogo()
    por_codigo = _por_codigo(catalogo)
    propias = [por_codigo[codigo] for codigo in ("42300", "42301", "42302", "42310", "42311", "42312")]
    assert curso_del_alumno(propias) is None


def prueba_laura_tiene_su_matricula_real_y_curso_tercero():
    catalogo = _catalogo()
    matriculas = RepositorioMatriculasMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    asignaturas.reemplazar(catalogo)
    matriculas.reemplazar_alumno(EMAIL_LAURA, list(CODIGOS_LAURA), dict(GRUPOS_LAURA))
    resultado = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar(EMAIL_LAURA)
    assert {asignatura.codigo for asignatura in resultado.asignaturas} == set(CODIGOS_LAURA)
    assert resultado.curso == CursoAsignatura.TERCERO
    assert sum(tramo.porcentaje for tramo in resultado.tramos) == 100
    assert any(tramo.curso == CursoAsignatura.TERCERO and tramo.cantidad == 6 for tramo in resultado.tramos)
    assert matriculas.obtener_grupos(EMAIL_LAURA) == dict(GRUPOS_LAURA)
    assert resultado.creditos_aprobados == 0
    assert resultado.media is None


def prueba_una_cuenta_nueva_empieza_sin_matricula():
    catalogo = _catalogo()
    matriculas = RepositorioMatriculasMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    asignaturas.reemplazar(catalogo)
    email = "nueva@ejemplo.com"
    resultado = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar(email)
    assert resultado.asignaturas == []
    assert resultado.horario == []
    assert matriculas.obtener_codigos(email) == []


def prueba_dos_cuentas_nuevas_quedan_vacias_hasta_que_editen():
    catalogo = _catalogo()
    matriculas = RepositorioMatriculasMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    asignaturas.reemplazar(catalogo)
    una = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar("una@ejemplo.com")
    otra = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar("otra@ejemplo.com")
    assert una.asignaturas == []
    assert otra.asignaturas == []
