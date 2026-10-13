from abc import ABC, abstractmethod


class EnviadorCorreo(ABC):
    @abstractmethod
    def enviar(self, destino: str, asunto: str, cuerpo: str) -> None: ...
