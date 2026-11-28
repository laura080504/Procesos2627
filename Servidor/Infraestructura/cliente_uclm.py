import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from Servidor.Dominio.DominioExceptions.oauth_no_valido import OauthNoValido

URL_AUTORIZACION_DEFECTO = "https://adas.uclm.es/OAUTH2/authserver.php"
URL_TOKEN_DEFECTO = "https://adas.uclm.es/OAUTH2/token.php"
URL_PERFIL_DEFECTO = "https://adas.uclm.es/OAUTH2/userinfo.php"


class ClienteUclm:
    def __init__(
        self,
        endpoint_autorizacion: str = URL_AUTORIZACION_DEFECTO,
        endpoint_token: str = URL_TOKEN_DEFECTO,
        endpoint_perfil: str = URL_PERFIL_DEFECTO,
    ):
        self.endpoint_autorizacion = (endpoint_autorizacion or URL_AUTORIZACION_DEFECTO).rstrip("/")
        self.endpoint_token = (endpoint_token or URL_TOKEN_DEFECTO).rstrip("/")
        self.endpoint_perfil = (endpoint_perfil or URL_PERFIL_DEFECTO).rstrip("/")

    def url_autorizacion(
        self,
        client_id: str,
        redirect_uri: str,
        estado: str,
        code_challenge: str | None = None,
    ) -> str:
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": estado,
        }
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        return f"{self.endpoint_autorizacion}?{urlencode(params)}"

    def perfil(
        self,
        code: str,
        redirect_uri: str,
        client_id: str,
        client_secret: str,
        code_verifier: str | None = None,
    ) -> dict:
        cuerpo_dict = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        if code_verifier:
            cuerpo_dict["code_verifier"] = code_verifier
        cuerpo = urlencode(cuerpo_dict).encode()
        try:
            token = self._leer(self.endpoint_token, cuerpo)
            acceso = token.get("access_token")
            if not acceso:
                raise OauthNoValido()
            return self._leer(self.endpoint_perfil, cabeceras={"Authorization": f"Bearer {acceso}"})
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, KeyError) as error:
            raise OauthNoValido() from error

    def _leer(self, url: str, cuerpo: bytes | None = None, cabeceras: dict | None = None) -> dict:
        peticion = Request(url, data=cuerpo, headers=cabeceras or {}, method="POST" if cuerpo else "GET")
        with urlopen(peticion, timeout=20) as respuesta:
            return json.load(respuesta)
