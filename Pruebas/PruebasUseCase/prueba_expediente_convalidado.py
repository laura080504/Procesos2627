from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioServices.expediente_alumno import expediente_de
from Servidor.Dominio.DominioUseCases.asegurar_catalogo_asignaturas_use_case import AsegurarCatalogoAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.obtener_matricula_use_case import ObtenerMatriculaUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas_memoria import RepositorioAsignaturasMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos_memoria import RepositorioCursosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas_memoria import RepositorioMatriculasMemoria


def _asignatura(codigo, curso, creditos=6):
    from Servidor.Dominio.DominioEntities.asignatura import Asignatura

    return Asignatura(codigo, codigo, codigo, curso, creditos, 1)


def prueba_convalidada_suma_creditos_y_no_entra_en_la_media():
    # Misma tabla que la cara A del examen, con B convalidada.
    asignaturas = [
        _asignatura("A", CursoAsignatura.PRIMERO, 6),
        _asignatura("B", CursoAsignatura.PRIMERO, 6),
        _asignatura("C", CursoAsignatura.SEGUNDO, 12),
        _asignatura("D", CursoAsignatura.SEGUNDO, 6),
    ]
    notas = {"A": 4.0, "B": 9.0, "C": 6.5, "D": None}
    expediente = expediente_de(asignaturas, notas, convalidadas={"B"})

    # Aprobados: A no (4), B convalidada (6), C sí (12), D sin nota → 18
    assert expediente.creditos_aprobados == 18
    assert expediente.creditos_convalidados == 6
    # Media solo A y C: (4*6 + 6.5*12) / (6+12) = 102 / 18 = 5.67
    assert expediente.media == 5.67


def prueba_alumno_solo_con_asignaturas_convalidadas_no_tiene_media():
    asignaturas = [
        _asignatura("A", CursoAsignatura.PRIMERO, 6),
        _asignatura("B", CursoAsignatura.SEGUNDO, 6),
    ]
    expediente = expediente_de(asignaturas, {"A": None, "B": None}, convalidadas={"A", "B"})

    assert expediente.creditos_aprobados == 12
    assert expediente.creditos_convalidados == 12
    assert expediente.media is None


def prueba_matricula_expone_creditos_convalidados():
    cursos = RepositorioCursosMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    AsegurarCatalogoAsignaturasUseCase(cursos, asignaturas).ejecutar()
    matriculas = RepositorioMatriculasMemoria()
    email = "convalidada@ejemplo.com"
    matriculas.reemplazar_alumno(email, ["42300", "42302", "42305"])
    matriculas.rellenar_notas(email, {"42300": 7.0, "42302": 8.0, "42305": 4.0})
    matriculas.marcar_convalidadas(email, ["42305"])

    resultado = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar(email)

    # 42300 y 42302 aprobadas (12) + 42305 convalidada (6) = 18
    assert resultado.creditos_aprobados == 18
    assert resultado.creditos_convalidados == 6
    # Media solo de 42300 y 42302: (7*6 + 8*6) / 12 = 7.5
    assert resultado.media == 7.5
    assert matriculas.obtener_notas(email)["42305"] is None
    assert "42305" in matriculas.obtener_convalidadas(email)
