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
        return calculo is not None and calculo.hora == "09:00" and calculo.lugar == "Aula Multiusos"
