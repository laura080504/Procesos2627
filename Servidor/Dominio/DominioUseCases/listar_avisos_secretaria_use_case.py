from Servidor.Dominio.DominioEntities.aviso_secretaria import AvisoSecretaria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_avisos_secretaria import (
    RepositorioAvisosSecretaria,
)


class ListarAvisosSecretariaUseCase:
    def __init__(self, repositorio: RepositorioAvisosSecretaria):
        self.repositorio = repositorio

    def ejecutar(self) -> list[AvisoSecretaria]:
        return [aviso for aviso in self.repositorio.obtener_todos() if aviso.id]
