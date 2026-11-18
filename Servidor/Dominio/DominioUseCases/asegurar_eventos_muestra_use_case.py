from datetime import date

from Servidor.Dominio.DominioServices.eventos_muestra import generar_eventos_muestra
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos


class AsegurarEventosMuestraUseCase:
    def __init__(self, repositorio_eventos: RepositorioEventos, repositorio_asignaturas: RepositorioAsignaturas):
        self.repositorio_eventos = repositorio_eventos
        self.repositorio_asignaturas = repositorio_asignaturas

    def ejecutar(self) -> None:
        asignaturas = self.repositorio_asignaturas.obtener_todas()
        if not asignaturas:
            return
        if self._ya_tienen_detalle():
            return
        self.repositorio_eventos.reemplazar(generar_eventos_muestra(asignaturas))

    def _ya_tienen_detalle(self) -> bool:
        eventos = self.repositorio_eventos.obtener_todos()
        if not eventos:
            return False
        calculo = next(
            (
                evento
                for evento in eventos
                if evento.fecha == date(2026, 10, 11) and evento.codigo == "42300"
            ),
            None,
        )
        if calculo is None or calculo.hora != "09:00" or calculo.lugar != "Aula Multiusos":
            return False
        # Fuerza regenerar cuando faltan los avisos de noviembre de la matrícula demo.
        gestion = next(
            (
                evento
                for evento in eventos
                if evento.fecha == date(2026, 11, 19) and evento.codigo == "42304"
            ),
            None,
        )
        return gestion is not None and gestion.hora == "23:59"
