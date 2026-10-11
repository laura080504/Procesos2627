import os
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@dataclass(frozen=True)
class Configuracion:
    duracion_sesion: timedelta
    cookie_segura: bool
    motor_datos: str
    nivel_registro: str = "INFO"
    admin_email: str | None = None
    admin_contrasena: str | None = field(default=None, repr=False)
    nombre_cookie_sesion: str = "sesion"
    mongo_uri: str | None = field(default=None, repr=False)
    mongo_db: str = "procesos"
    mongo_usuario: str | None = None
    mongo_contrasena: str | None = field(default=None, repr=False)


def cargar_configuracion() -> Configuracion:
    motor = os.getenv("DATOS_MOTOR", "memoria")
    if motor not in {"memoria", "mongo"}:
        raise ValueError("DATOS_MOTOR debe ser memoria o mongo.")
    mongo_uri = os.getenv("MONGO_URI", "").strip() or None
    mongo_db = os.getenv("MONGO_DB", "procesos").strip() or "procesos"
    mongo_usuario = os.getenv("MONGO_USUARIO", "").strip() or None
    mongo_contrasena = os.getenv("MONGO_CONTRASENA", "") or None
    if motor == "mongo" and not mongo_uri:
        raise ValueError("MONGO_URI es obligatorio cuando DATOS_MOTOR es mongo.")
    if motor == "mongo" and bool(mongo_usuario) != bool(mongo_contrasena):
        raise ValueError("MONGO_USUARIO y MONGO_CONTRASENA deben indicarse juntos.")
    if motor == "mongo" and mongo_uri and not _uri_tiene_credenciales(mongo_uri) and not mongo_usuario:
        raise ValueError(
            "MONGO_USUARIO y MONGO_CONTRASENA son obligatorios si MONGO_URI no incluye credenciales."
        )
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
        motor_datos=motor,
        nivel_registro=nivel,
        admin_email=admin_email or None,
        admin_contrasena=admin_contrasena or None,
        mongo_uri=mongo_uri,
        mongo_db=mongo_db,
        mongo_usuario=mongo_usuario,
        mongo_contrasena=mongo_contrasena,
    )


def _uri_tiene_credenciales(uri: str) -> bool:
    autoridad = uri.split("://", 1)[-1].split("/")[0]
    return "@" in autoridad
