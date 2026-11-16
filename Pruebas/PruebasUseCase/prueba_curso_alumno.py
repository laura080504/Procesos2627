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
    assert resultado.creditos_aprobados == 30
    assert resultado.media == 7.0


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


def prueba_una_cuenta_nueva_recibe_matricula_aleatoria_al_acceder():
    catalogo = _catalogo()
    matriculas = RepositorioMatriculasMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    asignaturas.reemplazar(catalogo)
    email = "nueva@ejemplo.com"
    resultado = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar(email)
    codigos = {asignatura.codigo for asignatura in resultado.asignaturas}
    assert len(codigos) == 6
    assert all(codigo in {asignatura.codigo for asignatura in catalogo} for codigo in codigos)
    assert all(nota is not None for nota in matriculas.obtener_notas(email).values())
    repetido = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar(email)
    assert {asignatura.codigo for asignatura in repetido.asignaturas} == codigos


def prueba_dos_cuentas_nuevas_no_comparten_la_misma_matricula():
    catalogo = _catalogo()
    matriculas = RepositorioMatriculasMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    asignaturas.reemplazar(catalogo)
    una = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar("una@ejemplo.com")
    otra = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar("otra@ejemplo.com")
    assert {asignatura.codigo for asignatura in una.asignaturas} != {
        asignatura.codigo for asignatura in otra.asignaturas
    }
