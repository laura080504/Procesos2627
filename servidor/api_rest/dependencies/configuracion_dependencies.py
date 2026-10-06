from functools import lru_cache

from servidor.configuracion import Configuracion, cargar_configuracion
from servidor.dominio.services.hasher_contrasenas import HasherContrasenas


@lru_cache
def obtener_configuracion() -> Configuracion:
    return cargar_configuracion()


@lru_cache
def obtener_hasher_contrasenas() -> HasherContrasenas:
    return HasherContrasenas()
