import smtplib
from email.message import EmailMessage

from Servidor.Dominio.DominioExceptions.correo_no_enviado import CorreoNoEnviado
from Servidor.Infraestructura.enviador_correo import EnviadorCorreo


class EnviadorCorreoBrevo(EnviadorCorreo):
    def __init__(
        self,
        servidor: str,
        puerto: int,
        usuario: str | None,
        clave: str | None,
        remitente: str | None,
        nombre: str,
    ):
        self.servidor = servidor
        self.puerto = puerto
        self.usuario = usuario
        self.clave = clave
        self.remitente = remitente
        self.nombre = nombre

    def enviar(self, destino: str, asunto: str, cuerpo: str) -> None:
        if not self.usuario or not self.clave or not self.remitente:
            raise CorreoNoEnviado("El envío de correo no está configurado")
        mensaje = EmailMessage()
        mensaje["From"] = f"{self.nombre} <{self.remitente}>"
        mensaje["To"] = destino
        mensaje["Subject"] = asunto
        mensaje.set_content(cuerpo)
        try:
            with smtplib.SMTP(self.servidor, self.puerto, timeout=30) as smtp:
                smtp.starttls()
                smtp.login(self.usuario, self.clave)
                smtp.send_message(mensaje)
        except (OSError, smtplib.SMTPException) as error:
            raise CorreoNoEnviado("No se ha podido enviar el correo de confirmación") from error
