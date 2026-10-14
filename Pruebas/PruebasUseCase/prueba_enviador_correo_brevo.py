import json

import pytest

from Servidor.Dominio.DominioExceptions.correo_no_enviado import CorreoNoEnviado
from Servidor.Infraestructura.enviador_correo_brevo import URL_API, EnviadorCorreoBrevo


class _Respuesta:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def prueba_envia_la_confirmacion_por_https(monkeypatch):
    capturado = {}

    def falso(peticion, timeout):
        capturado["url"] = peticion.full_url
        capturado["cuerpo"] = json.loads(peticion.data)
        capturado["clave"] = peticion.get_header("Api-key")
        capturado["timeout"] = timeout
        return _Respuesta()

    monkeypatch.setattr("Servidor.Infraestructura.enviador_correo_brevo.urlopen", falso)
    EnviadorCorreoBrevo("clave-api", "remitente@ejemplo.com", "procesos2627").enviar(
        "destino@ejemplo.com", "Confirma tu cuenta", "Hola"
    )

    assert capturado["url"] == URL_API
    assert capturado["clave"] == "clave-api"
    assert capturado["cuerpo"]["sender"] == {"name": "procesos2627", "email": "remitente@ejemplo.com"}
    assert capturado["cuerpo"]["to"] == [{"email": "destino@ejemplo.com"}]
    assert capturado["cuerpo"]["textContent"] == "Hola"


def prueba_sin_clave_api_no_intenta_enviar():
    with pytest.raises(CorreoNoEnviado, match="no está configurado"):
        EnviadorCorreoBrevo(None, "remitente@ejemplo.com", "procesos2627").enviar("a@b.com", "Asunto", "Hola")
