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
    matriculas = RepositorioMatriculasMemoria()
    return matriculas, asignaturas


def prueba_historial_manual_actualiza_media_y_pendientes():
    matriculas, asignaturas = _repos()
    email = "historial@ejemplo.com"
    matriculas.reemplazar_alumno(email, ["42322", "42324"], {"42322": "11", "42324": "11"})

    obtener = ObtenerExpedienteUseCase(matriculas, asignaturas)
    guardar = GuardarExpedienteUseCase(matriculas, asignaturas, obtener)
    vista = guardar.ejecutar(
        email,
        [
            CalificacionEntrada("42300", 7.5, False),
            CalificacionEntrada("42302", 8.0, False),
            CalificacionEntrada("42305", None, True),
        ],
    )

    assert vista.media == 7.75
    assert vista.creditos_aprobados == 18
    assert vista.creditos_convalidados == 6
    assert {item.codigo for item in vista.calificadas} == {"42300", "42302", "42305"}
    assert "42322" in {item.codigo for item in vista.pendientes}
    assert "42300" not in {item.codigo for item in vista.pendientes}

    # Matrícula activa intacta; perfil toma media del historial.
    matricula = ObtenerMatriculaUseCase(matriculas, asignaturas).ejecutar(email)
    assert {a.codigo for a in matricula.asignaturas} == {"42322", "42324"}
    assert matricula.media == 7.75
    assert matricula.creditos_aprobados == 18


def prueba_editar_matricula_conserva_notas_del_historial():
    matriculas, asignaturas = _repos()
    email = "conserva@ejemplo.com"
    matriculas.reemplazar_alumno(email, ["42322"], {"42322": "11"})
    obtener = ObtenerExpedienteUseCase(matriculas, asignaturas)
    GuardarExpedienteUseCase(matriculas, asignaturas, obtener).ejecutar(
        email,
        [CalificacionEntrada("42300", 9.0, False)],
    )
    matriculas.reemplazar_alumno(email, ["42322", "42324"], {"42322": "11", "42324": "11"})

    assert matriculas.obtener_notas(email)["42300"] == 9.0
    assert set(matriculas.obtener_codigos(email)) == {"42322", "42324"}
