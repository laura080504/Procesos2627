from pydantic import BaseModel


class RecuperacionSalida(BaseModel):
    mensaje: str = "Si el correo está registrado, recibirás instrucciones"
