from Servidor.Dominio.DominioEnums.intensificacion import Intensificacion
from Servidor.Dominio.DominioServices.matriculas_muestra import (
    EMAIL_LAURA,
    asegurar_matricula_de,
    forzar_matricula_laura,
)
from Servidor.Dominio.DominioUseCases.asegurar_catalogo_asignaturas_use_case import AsegurarCatalogoAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.guardar_expediente_use_case import CalificacionEntrada, GuardarExpedienteUseCase
from Servidor.Dominio.DominioUseCases.obtener_expediente_use_case import ObtenerExpedienteUseCase
from Servidor.Dominio.DominioUseCases.obtener_matricula_use_case import ObtenerMatriculaUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas_memoria import (
    RepositorioAsignaturasMemoria,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos_memoria import RepositorioCursosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas_memoria import RepositorioMatriculasMemoria


def _repos():
    cursos = RepositorioCursosMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    AsegurarCatalogoAsignaturasUseCase(cursos, asignaturas).ejecutar()
    return RepositorioMatriculasMemoria(), asignaturas


def prueba_laura_intensificacion_software_excluye_otras_ramas():
    matriculas, asignaturas = _repos()
    forzar_matricula_laura(matriculas)
    # Notas de prueba inventadas (no reales): solo para cubrir el filtro de mención.
    obtener = ObtenerExpedienteUseCase(matriculas, asignaturas)
    GuardarExpedienteUseCase(matriculas, asignaturas, obtener).ejecutar(
        EMAIL_LAURA,
        [
            CalificacionEntrada("42300", 6.0, False),
            CalificacionEntrada("42305", 4.0, False),
            CalificacionEntrada("42331", 8.0, False),
        ],
        Intensificacion.SOFTWARE.value,
    )

    vista = obtener.ejecutar(EMAIL_LAURA)
    assert vista.intensificacion == Intensificacion.SOFTWARE.value
    assert "42334" not in {item.codigo for item in vista.pendientes}
    assert "42342" not in {item.codigo for item in vista.pendientes}
    assert "42350" not in {item.codigo for item in vista.pendientes}
    assert "42326" in {item.codigo for item in vista.pendientes}
    assert "42305" not in {item.codigo for item in vista.pendientes}

    matricula = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar(EMAIL_LAURA)
    assert matricula.intensificacion == Intensificacion.SOFTWARE.value


def prueba_asegurar_no_crea_notas_en_codigo():
    matriculas, _asignaturas = _repos()
    asegurar_matricula_de(matriculas, EMAIL_LAURA)
    assert matriculas.obtener_intensificacion(EMAIL_LAURA) == Intensificacion.SOFTWARE.value
    assert all(nota is None for nota in matriculas.obtener_notas(EMAIL_LAURA).values())
