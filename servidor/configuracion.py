import os
from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class Configuracion:
    duracion_sesion: timedelta
    cookie_segura: bool
    ruta_datos: str
    motor_datos: str
    nombre_cookie_sesion: str = "sesion"


def cargar_configuracion() -> Configuracion:
    motor = os.getenv("DATOS_MOTOR", "sqlite")
    if motor not in {"sqlite", "memoria"}:
        raise ValueError("DATOS_MOTOR debe ser sqlite o memoria.")
    return Configuracion(
        duracion_sesion=timedelta(hours=float(os.getenv("SESION_DURACION_HORAS", "8"))),
        cookie_segura=os.getenv("COOKIE_SEGURA", "false").lower() == "true",
        ruta_datos=os.getenv("DATOS_RUTA", "servidor/infraestructura/aplicacion.db"),
        motor_datos=motor,
    )
