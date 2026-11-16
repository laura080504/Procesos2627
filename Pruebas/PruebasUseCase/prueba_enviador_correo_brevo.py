import json
import smtplib

import pytest

from Servidor.Dominio.DominioExceptions.correo_no_enviado import CorreoNoEnviado
from Servidor.Infraestructura.enviador_correo_brevo import URL_API, EnviadorCorreoBrevo


class _Respuesta:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class _SmtpFalso:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.login_args = None
        self.mensaje = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def starttls(self):
        return None

    def login(self, usuario, clave):
        self.login_args = (usuario, clave)

    def send_message(self, mensaje):
        self.mensaje = mensaje


def _enviador(**kwargs):
    base = {
        "servidor": "smtp-relay.brevo.com",
        "puerto": 587,
        "usuario": "usuario@smtp-brevo.com",
        "clave_smtp": "clave-smtp",
        "remitente": "remitente@ejemplo.com",
        "nombre": "procesos2627",
        "api_clave": None,
    }
    base.update(kwargs)
    return EnviadorCorreoBrevo(**base)


def prueba_prioriza_la_api_si_hay_clave(monkeypatch):
    capturado = {}

    def falso(peticion, timeout):
        capturado["url"] = peticion.full_url
        capturado["cuerpo"] = json.loads(peticion.data)
        capturado["clave"] = peticion.get_header("Api-key")
        return _Respuesta()

    monkeypatch.setattr("Servidor.Infraestructura.enviador_correo_brevo.urlopen", falso)
    _enviador(api_clave="clave-api").enviar("destino@ejemplo.com", "Confirma tu cuenta", "Hola")

    assert capturado["url"] == URL_API
    assert capturado["clave"] == "clave-api"
    assert capturado["cuerpo"]["sender"] == {"name": "procesos2627", "email": "remitente@ejemplo.com"}
    assert capturado["cuerpo"]["to"] == [{"email": "destino@ejemplo.com"}]


def prueba_usa_smtp_si_no_hay_api(monkeypatch):
    capturado = {}

    def falso_smtp(servidor, puerto, timeout=None):
        smtp = _SmtpFalso(servidor, puerto, timeout=timeout)
        capturado["smtp"] = smtp
        return smtp

    monkeypatch.setattr("Servidor.Infraestructura.enviador_correo_brevo.smtplib.SMTP", falso_smtp)
    _enviador(api_clave=None).enviar("destino@ejemplo.com", "Confirma tu cuenta", "Hola")

    smtp = capturado["smtp"]
    assert smtp.args[:2] == ("smtp-relay.brevo.com", 587)
    assert smtp.login_args == ("usuario@smtp-brevo.com", "clave-smtp")
    assert smtp.mensaje["To"] == "destino@ejemplo.com"


def prueba_sin_credenciales_no_intenta_enviar():
    with pytest.raises(CorreoNoEnviado, match="no está configurado"):
        _enviador(api_clave=None, usuario=None, clave_smtp=None).enviar("a@b.com", "Asunto", "Hola")


def prueba_error_smtp_se_traduce(monkeypatch):
    class _SmtpFalla:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def starttls(self):
            return None

        def login(self, *args):
            raise smtplib.SMTPAuthenticationError(535, b"auth")

        def send_message(self, mensaje):
            return None

    monkeypatch.setattr("Servidor.Infraestructura.enviador_correo_brevo.smtplib.SMTP", _SmtpFalla)
    with pytest.raises(CorreoNoEnviado, match="No se ha podido enviar"):
        _enviador(api_clave=None).enviar("a@b.com", "Asunto", "Hola")
