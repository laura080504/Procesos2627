import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from Servidor.Dominio.DominioExceptions.correo_no_enviado import CorreoNoEnviado
from Servidor.Infraestructura.enviador_correo import EnviadorCorreo

URL_API = "https://api.brevo.com/v3/smtp/email"


class EnviadorCorreoBrevo(EnviadorCorreo):
    def __init__(self, api_clave: str | None, remitente: str | None, nombre: str):
        self.api_clave = api_clave
        self.remitente = remitente
        self.nombre = nombre

    def enviar(self, destino: str, asunto: str, cuerpo: str) -> None:
        if not self.api_clave or not self.remitente:
            raise CorreoNoEnviado("El envío de correo no está configurado")
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
