import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from Servidor.Dominio.DominioExceptions.oauth_no_valido import OauthNoValido

URL_AUTORIZACION = "https://accounts.google.com/o/oauth2/v2/auth"
URL_TOKEN = "https://oauth2.googleapis.com/token"
URL_PERFIL = "https://openidconnect.googleapis.com/v1/userinfo"


class ClienteGoogle:
    def url_autorizacion(self, client_id: str, redirect_uri: str, estado: str) -> str:
        consulta = urlencode(
            {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "state": estado,
                "prompt": "select_account",
            }
        )
        return f"{URL_AUTORIZACION}?{consulta}"

    def perfil(self, code: str, redirect_uri: str, client_id: str, client_secret: str) -> dict:
        cuerpo = urlencode(
            {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
        ).encode()
        try:
            token = self._leer(URL_TOKEN, cuerpo)
            acceso = token.get("access_token")
            if not acceso:
                raise OauthNoValido()
            return self._leer(URL_PERFIL, cabeceras={"Authorization": f"Bearer {acceso}"})
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, KeyError) as error:
            raise OauthNoValido() from error

    def _leer(self, url: str, cuerpo: bytes | None = None, cabeceras: dict | None = None) -> dict:
        peticion = Request(url, data=cuerpo, headers=cabeceras or {}, method="POST" if cuerpo else "GET")
        with urlopen(peticion, timeout=20) as respuesta:
            return json.load(respuesta)
