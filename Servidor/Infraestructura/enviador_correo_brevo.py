import json
import smtplib
from email.message import EmailMessage
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from Servidor.Dominio.DominioExceptions.correo_no_enviado import CorreoNoEnviado
from Servidor.Infraestructura.enviador_correo import EnviadorCorreo

URL_API = "https://api.brevo.com/v3/smtp/email"


class EnviadorCorreoBrevo(EnviadorCorreo):
    def __init__(
        self,
        servidor: str,
        puerto: int,
        usuario: str | None,
        clave_smtp: str | None,
        remitente: str | None,
        nombre: str,
        api_clave: str | None = None,
    ):
        self.servidor = servidor
        self.puerto = puerto
        self.usuario = usuario
        self.clave_smtp = clave_smtp
        self.remitente = remitente
        self.nombre = nombre
        self.api_clave = api_clave

    def enviar(self, destino: str, asunto: str, cuerpo: str) -> None:
        if not self.remitente:
            raise CorreoNoEnviado("El envío de correo no está configurado")
        if self.api_clave:
            self._enviar_api(destino, asunto, cuerpo)
            return
        if self.usuario and self.clave_smtp:
            self._enviar_smtp(destino, asunto, cuerpo)
            return
        raise CorreoNoEnviado("El envío de correo no está configurado")

    def _enviar_api(self, destino: str, asunto: str, cuerpo: str) -> None:
        peticion = Request(
            URL_API,
            data=json.dumps(
                {
                    "sender": {"name": self.nombre, "email": self.remitente},
                    "to": [{"email": destino}],
                    "subject": asunto,
                    "textContent": cuerpo,
                }
            ).encode(),
            method="POST",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": self.api_clave,
            },
        )
        try:
            with urlopen(peticion, timeout=30):
                return
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            raise CorreoNoEnviado("No se ha podido enviar el correo de confirmación") from error

    def _enviar_smtp(self, destino: str, asunto: str, cuerpo: str) -> None:
        mensaje = EmailMessage()
        mensaje["From"] = f"{self.nombre} <{self.remitente}>"
        mensaje["To"] = destino
        mensaje["Subject"] = asunto
        mensaje.set_content(cuerpo)
        try:
            with smtplib.SMTP(self.servidor, self.puerto, timeout=30) as smtp:
                smtp.starttls()
                smtp.login(self.usuario, self.clave_smtp)
                smtp.send_message(mensaje)
        except (OSError, smtplib.SMTPException) as error:
            raise CorreoNoEnviado("No se ha podido enviar el correo de confirmación") from error
