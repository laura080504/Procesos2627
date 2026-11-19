from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioServices.matriculas_muestra import CODIGOS_LAURA, EMAIL_LAURA
from Servidor.Dominio.DominioUseCases.asegurar_catalogo_asignaturas_use_case import AsegurarCatalogoAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.guardar_matricula_use_case import (
    AsignaturaMatriculaEntrada,
    GuardarMatriculaUseCase,
)
from Servidor.Dominio.DominioUseCases.obtener_matricula_use_case import ObtenerMatriculaUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas_memoria import (
    RepositorioAsignaturasMemoria,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos_memoria import RepositorioCursosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas_memoria import (
    RepositorioMatriculasMemoria,
)


def _casos():
    cursos = RepositorioCursosMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    AsegurarCatalogoAsignaturasUseCase(cursos, asignaturas).ejecutar()
    matriculas = RepositorioMatriculasMemoria()
    matriculas.reemplazar_alumno(EMAIL_LAURA, list(CODIGOS_LAURA), {codigo: "A" for codigo in CODIGOS_LAURA})
    obtener = ObtenerMatriculaUseCase(matriculas, asignaturas)
    guardar = GuardarMatriculaUseCase(matriculas, asignaturas, obtener)
    return matriculas, guardar


def prueba_guardar_matricula_reemplaza_codigos_y_grupos():
    matriculas, guardar = _casos()
    resultado = guardar.ejecutar(
        EMAIL_LAURA,
        [
            AsignaturaMatriculaEntrada("42300", "B"),
            AsignaturaMatriculaEntrada("42314", "A"),
            AsignaturaMatriculaEntrada("42322", "C"),
        ],
    )
    assert [asignatura.codigo for asignatura in resultado.asignaturas] == ["42300", "42314", "42322"]
    assert matriculas.obtener_grupos(EMAIL_LAURA) == {
        "42300": "B",
        "42314": "A",
        "42322": "C",
    }
    assert set(matriculas.obtener_codigos(EMAIL_LAURA)) == {"42300", "42314", "42322"}
    for franja in resultado.horario:
        assert franja.grupo == matriculas.obtener_grupos(EMAIL_LAURA)[franja.codigo]


def prueba_guardar_matricula_rechaza_codigo_desconocido():
    _, guardar = _casos()
    try:
        guardar.ejecutar(EMAIL_LAURA, [AsignaturaMatriculaEntrada("99999", "A")])
        assert False, "debía fallar"
    except EstadoNoValido as error:
        assert "99999" in str(error)
