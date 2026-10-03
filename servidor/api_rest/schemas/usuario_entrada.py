from pydantic import BaseModel, Field


class UsuarioEntrada(BaseModel):
    nick: str = Field(min_length=1, max_length=30)
