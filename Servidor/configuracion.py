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
    secretaria_email: str | None = None
    secretaria_contrasena: str | None = field(default=None, repr=False)
    nombre_cookie_sesion: str = "sesion"
    mongo_uri: str | None = field(default=None, repr=False)
    mongo_db: str = "procesos"
    mongo_usuario: str | None = None
    mongo_contrasena: str | None = field(default=None, repr=False)
    brevo_smtp_servidor: str = "smtp-relay.brevo.com"
    brevo_smtp_puerto: int = 587
    brevo_smtp_usuario: str | None = None
    brevo_smtp_clave: str | None = field(default=None, repr=False)
    brevo_remitente: str | None = None
    brevo_remitente_nombre: str = "procesos2627"
    brevo_api_clave: str | None = field(default=None, repr=False)
    google_client_id: str | None = None
    google_client_secret: str | None = field(default=None, repr=False)
    url_publica: str | None = None
    horarios_esiiab_vivo: bool = True
    horarios_esiiab_url: str = "https://esiiab.uclm.es/horarios/"
    horarios_esiiab_ttl_segundos: int = 30 * 60


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
    secretaria_email = os.getenv("SECRETARIA_EMAIL", "").strip().lower()
    secretaria_contrasena = os.getenv("SECRETARIA_PASSWORD", "")
    if bool(secretaria_email) != bool(secretaria_contrasena):
        raise ValueError("SECRETARIA_EMAIL y SECRETARIA_PASSWORD deben indicarse juntos.")
    if secretaria_contrasena and not 8 <= len(secretaria_contrasena) <= 64:
        raise ValueError("SECRETARIA_PASSWORD debe tener entre 8 y 64 caracteres.")
    if admin_email and secretaria_email and admin_email == secretaria_email:
        raise ValueError("ADMIN_EMAIL y SECRETARIA_EMAIL deben ser correos distintos.")
    google_client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip() or None
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "") or None
    if bool(google_client_id) != bool(google_client_secret):
        raise ValueError("GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET deben indicarse juntos.")
    url_publica = os.getenv("URL_PUBLICA", "").strip().rstrip("/") or None
    horarios_vivo = os.getenv("HORARIOS_ESIIAB_VIVO", "true").lower() != "false"
    horarios_url = os.getenv("HORARIOS_ESIIAB_URL", "https://esiiab.uclm.es/horarios/").strip()
    horarios_ttl = int(os.getenv("HORARIOS_ESIIAB_TTL_SEGUNDOS", str(30 * 60)))
    return Configuracion(
        duracion_sesion=timedelta(hours=float(os.getenv("SESION_DURACION_HORAS", "8"))),
        cookie_segura=os.getenv("COOKIE_SEGURA", "false").lower() == "true",
        motor_datos=motor,
        nivel_registro=nivel,
        admin_email=admin_email or None,
        admin_contrasena=admin_contrasena or None,
        secretaria_email=secretaria_email or None,
        secretaria_contrasena=secretaria_contrasena or None,
        mongo_uri=mongo_uri,
        mongo_db=mongo_db,
        mongo_usuario=mongo_usuario,
        mongo_contrasena=mongo_contrasena,
        brevo_smtp_servidor=os.getenv("BREVO_SMTP_SERVIDOR", "smtp-relay.brevo.com"),
        brevo_smtp_puerto=int(os.getenv("BREVO_SMTP_PUERTO", "587")),
        brevo_smtp_usuario=os.getenv("BREVO_SMTP_USUARIO", "").strip() or None,
        brevo_smtp_clave=os.getenv("BREVO_SMTP_CLAVE", "") or None,
        brevo_remitente=os.getenv("BREVO_REMITENTE", "").strip() or None,
        brevo_remitente_nombre=os.getenv("BREVO_REMITENTE_NOMBRE", "procesos2627").strip() or "procesos2627",
        brevo_api_clave=os.getenv("BREVO_API_CLAVE", "") or None,
        google_client_id=google_client_id,
        google_client_secret=google_client_secret or None,
        url_publica=url_publica,
        horarios_esiiab_vivo=horarios_vivo,
        horarios_esiiab_url=horarios_url or "https://esiiab.uclm.es/horarios/",
        horarios_esiiab_ttl_segundos=max(30, horarios_ttl),
    )


def _uri_tiene_credenciales(uri: str) -> bool:
    autoridad = uri.split("://", 1)[-1].split("/")[0]
    return "@" in autoridad
