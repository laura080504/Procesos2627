from pydantic import BaseModel, EmailStr


class RecuperacionEntrada(BaseModel):
    email: EmailStr
