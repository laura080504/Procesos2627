import smtplib

import pytest

from Servidor.Dominio.DominioExceptions.correo_no_enviado import CorreoNoEnviado
from Servidor.Infraestructura.enviador_correo_brevo import EnviadorCorreoBrevo


class _SmtpFalso:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
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


def prueba_envia_la_confirmacion_por_smtp(monkeypatch):
    capturado = {}

    def falso_smtp(servidor, puerto, timeout=None):
        smtp = _SmtpFalso(servidor, puerto, timeout=timeout)
        capturado["smtp"] = smtp
        return smtp

    monkeypatch.setattr("Servidor.Infraestructura.enviador_correo_brevo.smtplib.SMTP", falso_smtp)
    EnviadorCorreoBrevo(
        "smtp-relay.brevo.com",
        587,
        "usuario@smtp-brevo.com",
        "clave-smtp",
        "remitente@ejemplo.com",
        "procesos2627",
    ).enviar("destino@ejemplo.com", "Confirma tu cuenta", "Hola")

    smtp = capturado["smtp"]
    assert smtp.args[:2] == ("smtp-relay.brevo.com", 587)
    assert smtp.login_args == ("usuario@smtp-brevo.com", "clave-smtp")
    assert smtp.mensaje["From"] == "procesos2627 <remitente@ejemplo.com>"
    assert smtp.mensaje["To"] == "destino@ejemplo.com"
    assert smtp.mensaje["Subject"] == "Confirma tu cuenta"
    assert smtp.mensaje.get_content().strip() == "Hola"


def prueba_sin_clave_smtp_no_intenta_enviar():
    with pytest.raises(CorreoNoEnviado, match="no está configurado"):
        EnviadorCorreoBrevo(
            "smtp-relay.brevo.com",
            587,
            "usuario@smtp-brevo.com",
            None,
            "remitente@ejemplo.com",
            "procesos2627",
        ).enviar("a@b.com", "Asunto", "Hola")


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
        EnviadorCorreoBrevo(
            "smtp-relay.brevo.com",
            587,
            "usuario@smtp-brevo.com",
            "clave-smtp",
            "remitente@ejemplo.com",
            "procesos2627",
        ).enviar("a@b.com", "Asunto", "Hola")
