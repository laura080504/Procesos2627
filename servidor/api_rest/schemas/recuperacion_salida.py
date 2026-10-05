from pydantic import BaseModel


class RecuperacionSalida(BaseModel):
    token: str
