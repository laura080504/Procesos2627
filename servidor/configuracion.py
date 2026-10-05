import os
from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class Configuracion:
    duracion_sesion: timedelta
    cookie_segura: bool
    nombre_cookie_sesion: str = "sesion"


def cargar_configuracion() -> Configuracion:
    return Configuracion(
        duracion_sesion=timedelta(hours=float(os.getenv("SESION_DURACION_HORAS", "8"))),
        cookie_segura=os.getenv("COOKIE_SEGURA", "false").lower() == "true",
    )
