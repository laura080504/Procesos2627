from Servidor.Dominio.DominioServices.eventos_muestra import generar_eventos_muestra
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos


class AsegurarEventosMuestraUseCase:
    def __init__(self, repositorio_eventos: RepositorioEventos, repositorio_asignaturas: RepositorioAsignaturas):
        self.repositorio_eventos = repositorio_eventos
        self.repositorio_asignaturas = repositorio_asignaturas

    def ejecutar(self) -> None:
        if self.repositorio_eventos.obtener_todos():
            return
        asignaturas = self.repositorio_asignaturas.obtener_todas()
        if not asignaturas:
            return
        self.repositorio_eventos.reemplazar(generar_eventos_muestra(asignaturas))
