from Servidor.Dominio.DominioUseCases.obtener_destinatarios_aviso_use_case import (
    ObtenerDestinatariosAvisoUseCase,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas_memoria import (
    RepositorioMatriculasMemoria,
)


def prueba_solo_los_matriculados_en_la_asignatura_reciben_el_aviso():
    matriculas = RepositorioMatriculasMemoria()
    matriculas.reemplazar_alumno("alumno@ejemplo.com", ["42330"])
    matriculas.reemplazar_alumno("ajeno@ejemplo.com", ["42327"])
    destinatarios = ObtenerDestinatariosAvisoUseCase(matriculas).ejecutar(
        "42330", ["alumno@ejemplo.com", "ajeno@ejemplo.com", "sin-matricula@ejemplo.com"]
    )
    assert destinatarios == {"alumno@ejemplo.com"}


def prueba_sin_conexiones_no_hay_destinatarios():
    matriculas = RepositorioMatriculasMemoria()
    matriculas.reemplazar_alumno("alumno@ejemplo.com", ["42330"])
    assert ObtenerDestinatariosAvisoUseCase(matriculas).ejecutar("42330", []) == set()
