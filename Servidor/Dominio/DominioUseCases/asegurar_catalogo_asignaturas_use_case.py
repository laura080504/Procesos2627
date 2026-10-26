from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioServices.catalogo_informatica_albacete import CATALOGO_INFORMATICA_ALBACETE
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos import RepositorioCursos


class AsegurarCatalogoAsignaturasUseCase:
    def __init__(self, repositorio_cursos: RepositorioCursos, repositorio_asignaturas: RepositorioAsignaturas):
        self.repositorio_cursos = repositorio_cursos
        self.repositorio_asignaturas = repositorio_asignaturas

    def ejecutar(self) -> None:
        for asignatura in CATALOGO_INFORMATICA_ALBACETE:
            self.repositorio_cursos.guardar(asignatura)
        self.reconstruir()

    def reconstruir(self) -> None:
        reunidas = []
        for curso in CursoAsignatura:
            reunidas.extend(self.repositorio_cursos.obtener(curso.value))
        self.repositorio_asignaturas.reemplazar(reunidas)
