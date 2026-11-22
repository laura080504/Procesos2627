from collections.abc import Iterable

from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas


class ObtenerDestinatariosAvisoUseCase:
    """Decide qué alumnos conectados deben recibir el aviso de una asignatura."""

    def __init__(self, repositorio_matriculas: RepositorioMatriculas):
        self.repositorio_matriculas = repositorio_matriculas

    def ejecutar(self, codigo: str, emails: Iterable[str]) -> set[str]:
        return {
            email
            for email in emails
            if codigo in self.repositorio_matriculas.obtener_codigos(email)
        }
