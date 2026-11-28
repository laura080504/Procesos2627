from Servidor.Dominio.DominioServices.avisos_secretaria_muestra import AVISOS_ESIIAB_MUESTRA
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_avisos_secretaria import (
    RepositorioAvisosSecretaria,
)


class AsegurarAvisosSecretariaMuestraUseCase:
    """Siembra avisos públicos de https://esiiab.uclm.es/eventos/ si el almacén está vacío."""

    def __init__(self, repositorio: RepositorioAvisosSecretaria):
        self.repositorio = repositorio

    def ejecutar(self) -> None:
        if not self.repositorio.vacio():
            return
        for aviso in AVISOS_ESIIAB_MUESTRA:
            self.repositorio.guardar(aviso)
