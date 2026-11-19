from datetime import date

from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos


class AsegurarEventosMuestraUseCase:
    """Elimina la semilla ficticia de entregas/exámenes si aún está en la BBDD.

    El calendario y los exámenes oficiales vienen de ESIIAB; los avisos reales
    los publica el profesor. No volvemos a generar datos de muestra.
    """

    def __init__(self, repositorio_eventos: RepositorioEventos, repositorio_asignaturas: RepositorioAsignaturas):
        self.repositorio_eventos = repositorio_eventos
        self.repositorio_asignaturas = repositorio_asignaturas

    def ejecutar(self) -> None:
        eventos = self.repositorio_eventos.obtener_todos()
        if not eventos:
            return
        if self._tiene_semilla_demo(eventos):
            self.repositorio_eventos.reemplazar([])

    def _tiene_semilla_demo(self, eventos) -> bool:
        return any(
            (
                evento.fecha == date(2026, 10, 11)
                and evento.codigo == "42300"
                and evento.lugar == "Aula Multiusos"
            )
            or (evento.fecha == date(2026, 11, 19) and evento.codigo == "42304")
            or (evento.fecha == date(2026, 11, 21) and evento.codigo == "42322")
            for evento in eventos
        )
