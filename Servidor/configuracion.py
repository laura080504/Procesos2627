import os
from dataclasses import dataclass, field
from datetime import timedelta


@dataclass(frozen=True)
class Configuracion:
    duracion_sesion: timedelta
    cookie_segura: bool
    ruta_datos: str
    motor_datos: str
    nivel_registro: str = "INFO"
    admin_email: str | None = None
    admin_contrasena: str | None = field(default=None, repr=False)
    nombre_cookie_sesion: str = "sesion"


def cargar_configuracion() -> Configuracion:
    motor = os.getenv("DATOS_MOTOR", "sqlite")
    if motor not in {"sqlite", "memoria"}:
        raise ValueError("DATOS_MOTOR debe ser sqlite o memoria.")
    nivel = os.getenv("LOG_NIVEL", "INFO").upper()
    if nivel not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
        raise ValueError("LOG_NIVEL debe ser DEBUG, INFO, WARNING o ERROR.")
    admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    admin_contrasena = os.getenv("ADMIN_PASSWORD", "")
    if bool(admin_email) != bool(admin_contrasena):
        raise ValueError("ADMIN_EMAIL y ADMIN_PASSWORD deben indicarse juntos.")
    if admin_contrasena and not 8 <= len(admin_contrasena) <= 64:
        raise ValueError("ADMIN_PASSWORD debe tener entre 8 y 64 caracteres.")
    return Configuracion(
        duracion_sesion=timedelta(hours=float(os.getenv("SESION_DURACION_HORAS", "8"))),
        cookie_segura=os.getenv("COOKIE_SEGURA", "false").lower() == "true",
        ruta_datos=os.getenv("DATOS_RUTA", "Servidor/Infraestructura/aplicacion.db"),
        motor_datos=motor,
        nivel_registro=nivel,
        admin_email=admin_email or None,
        admin_contrasena=admin_contrasena or None,
    )
