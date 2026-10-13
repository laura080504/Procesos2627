from pydantic import BaseModel, Field


class ConfirmarEntrada(BaseModel):
    token: str = Field(min_length=1)
