from functools import lru_cache

from Servidor.configuracion import Configuracion, cargar_configuracion
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas


@lru_cache
def obtener_configuracion() -> Configuracion:
    return cargar_configuracion()


@lru_cache
def obtener_hasher_contrasenas() -> HasherContrasenas:
    return HasherContrasenas()
