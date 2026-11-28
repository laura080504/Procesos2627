from time import monotonic

from Servidor.Dominio.DominioQueries.obtener_marcas_calendario_query import ObtenerMarcasCalendarioQuery
from Servidor.Dominio.DominioServices.marcas_calendario import MarcaCalendario, marcas_del_mes
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_avisos_secretaria import (
    RepositorioAvisosSecretaria,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos
from Servidor.Infraestructura.sincronizador_esiiab import SincronizadorEsiiab

_TTL_CACHE_MARCAS = 120.0


class ObtenerMarcasCalendarioUseCase:
    def __init__(
        self,
        repositorio_eventos: RepositorioEventos,
        repositorio_asignaturas: RepositorioAsignaturas,
        sincronizador_esiiab: SincronizadorEsiiab | None = None,
        repositorio_avisos_secretaria: RepositorioAvisosSecretaria | None = None,
    ):
        self.repositorio_eventos = repositorio_eventos
        self.repositorio_asignaturas = repositorio_asignaturas
        self.sincronizador_esiiab = sincronizador_esiiab
        self.repositorio_avisos_secretaria = repositorio_avisos_secretaria
        self._cache: dict[tuple[int, int], tuple[float, list[MarcaCalendario]]] = {}
        self._catalogo_cache: tuple[float, dict] | None = None
        self._eventos_cache: tuple[float, list] | None = None
        self._avisos_cache: tuple[float, list] | None = None

    def invalidar_cache(self) -> None:
        self._cache.clear()
        self._catalogo_cache = None
        self._eventos_cache = None
        self._avisos_cache = None

    def ejecutar(self, query: ObtenerMarcasCalendarioQuery) -> list[MarcaCalendario]:
        clave = (query.anio, query.mes)
        ahora = monotonic()
        cacheada = self._cache.get(clave)
        if cacheada and ahora - cacheada[0] < _TTL_CACHE_MARCAS:
            return cacheada[1]

        asignaturas_por_codigo = self._catalogo(ahora)
        eventos = self._eventos(ahora)
        avisos = self._avisos(ahora)
        examenes = None
        calendario = None
        if self.sincronizador_esiiab is not None:
            examenes = self.sincronizador_esiiab.asegurar_examenes()
            calendario = self.sincronizador_esiiab.asegurar_calendario()
        marcas = marcas_del_mes(
            eventos,
            asignaturas_por_codigo,
            query.anio,
            query.mes,
            examenes=examenes,
            calendario=calendario,
            avisos_secretaria=avisos,
        )
        self._cache[clave] = (ahora, marcas)
        if len(self._cache) > 36:
            antiguas = sorted(self._cache.items(), key=lambda item: item[1][0])[:12]
            for vieja, _ in antiguas:
                self._cache.pop(vieja, None)
        return marcas

    def ejecutar_rango(self, anio: int, mes: int, cantidad: int) -> dict[str, list[MarcaCalendario]]:
        cantidad = max(1, min(cantidad, 14))
        resultado: dict[str, list[MarcaCalendario]] = {}
        cursor_anio, cursor_mes = anio, mes
        for _ in range(cantidad):
            marcas = self.ejecutar(ObtenerMarcasCalendarioQuery(cursor_anio, cursor_mes))
            resultado[f"{cursor_anio}-{cursor_mes}"] = marcas
            cursor_mes += 1
            if cursor_mes > 12:
                cursor_mes = 1
                cursor_anio += 1
        return resultado

    def _catalogo(self, ahora: float) -> dict:
        if self._catalogo_cache and ahora - self._catalogo_cache[0] < _TTL_CACHE_MARCAS:
            return self._catalogo_cache[1]
        catalogo = {
            asignatura.codigo: asignatura for asignatura in self.repositorio_asignaturas.obtener_todas()
        }
        self._catalogo_cache = (ahora, catalogo)
        return catalogo

    def _eventos(self, ahora: float) -> list:
        if self._eventos_cache and ahora - self._eventos_cache[0] < _TTL_CACHE_MARCAS:
            return self._eventos_cache[1]
        eventos = self.repositorio_eventos.obtener_todos()
        self._eventos_cache = (ahora, eventos)
        return eventos

    def _avisos(self, ahora: float) -> list:
        if self.repositorio_avisos_secretaria is None:
            return []
        if self._avisos_cache and ahora - self._avisos_cache[0] < _TTL_CACHE_MARCAS:
            return self._avisos_cache[1]
        avisos = self.repositorio_avisos_secretaria.obtener_todos()
        self._avisos_cache = (ahora, avisos)
        return avisos
