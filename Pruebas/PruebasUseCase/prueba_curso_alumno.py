from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioServices.curso_alumno import curso_del_alumno
from Servidor.Dominio.DominioServices.matriculas_muestra import CODIGOS_LAURA, EMAIL_LAURA, NOTAS_LAURA, notas_de_muestra
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


def prueba_laura_es_de_primero_porque_es_la_mayoria_de_sus_asignaturas():
    catalogo = _catalogo()
    matriculas = RepositorioMatriculasMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    asignaturas.reemplazar(catalogo)
    matriculas.reemplazar_alumno("lgonzarico@gmail.com", list(CODIGOS_LAURA))
    resultado = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar("lgonzarico@gmail.com")
    assert {asignatura.codigo for asignatura in resultado.asignaturas} == set(CODIGOS_LAURA)
    assert resultado.curso == CursoAsignatura.PRIMERO
    assert sum(tramo.porcentaje for tramo in resultado.tramos) == 100
    assert any(tramo.curso == CursoAsignatura.PRIMERO and tramo.cantidad == 4 for tramo in resultado.tramos)
    assert resultado.creditos_aprobados == 0
    assert resultado.media is None


def prueba_laura_ve_los_creditos_aprobados_y_la_media():
    catalogo = _catalogo()
    matriculas = RepositorioMatriculasMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    asignaturas.reemplazar(catalogo)
    matriculas.reemplazar_alumno(EMAIL_LAURA, list(CODIGOS_LAURA))
    matriculas.rellenar_notas(EMAIL_LAURA, notas_de_muestra(EMAIL_LAURA, CODIGOS_LAURA))
    resultado = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar(EMAIL_LAURA)
    assert matriculas.obtener_notas(EMAIL_LAURA)["42305"] == NOTAS_LAURA["42305"]
    assert resultado.creditos_aprobados == 30
    assert resultado.media == 7.0
