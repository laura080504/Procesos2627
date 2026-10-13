import logging

from Pruebas.conftest import CONTRASENA

REGISTRO = {"email": "nuevo@ejemplo.com", "nick": "nuevo", "contrasena": "contrasena-segura"}


def prueba_registro_devuelve_el_usuario_sin_contrasena(cliente):
    respuesta = cliente.post("/api/auth/registro", json=REGISTRO)
    assert respuesta.status_code == 201
    assert respuesta.json() == {
        "email": "nuevo@ejemplo.com",
        "nick": "nuevo",
        "rol": "usuario",
        "estado": "pendiente",
    }


def prueba_registro_guarda_el_usuario_en_el_repositorio(cliente, repositorio_usuarios):
    assert cliente.post("/api/auth/registro", json=REGISTRO).status_code == 201
    guardado = repositorio_usuarios.obtener_por_email(REGISTRO["email"])
    assert guardado is not None
    assert guardado.nick == REGISTRO["nick"]
    assert guardado.rol.value == "usuario"
    assert guardado.estado.value == "pendiente"
    assert guardado.contrasena_hash != REGISTRO["contrasena"]


def prueba_registro_duplicado_devuelve_409(cliente, repositorio_usuarios):
    assert cliente.post("/api/auth/registro", json=REGISTRO).status_code == 201
    original = repositorio_usuarios.obtener_por_email(REGISTRO["email"])
    respuesta = cliente.post(
        "/api/auth/registro",
        json={**REGISTRO, "nick": "otro", "contrasena": "otra-segura"},
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "Este correo ya está registrado"
    guardado = repositorio_usuarios.obtener_por_email(REGISTRO["email"])
    assert guardado.nick == original.nick
    assert guardado.contrasena_hash == original.contrasena_hash


def prueba_registro_con_datos_no_validos_devuelve_422(cliente):
    assert cliente.post("/api/auth/registro", json={**REGISTRO, "email": "no-es-email"}).status_code == 422
    assert cliente.post("/api/auth/registro", json={**REGISTRO, "contrasena": "corta"}).status_code == 422
    assert cliente.post("/api/auth/registro", json={**REGISTRO, "nick": "   "}).status_code == 422


def prueba_inicio_sesion_correcto_crea_cookie_httponly(cliente, usuario_registrado):
    respuesta = cliente.post(
        "/api/auth/inicio-sesion", json={"email": usuario_registrado.email, "contrasena": CONTRASENA}
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["email"] == usuario_registrado.email
    assert "httponly" in respuesta.headers["set-cookie"].lower()


def prueba_el_inicio_no_registra_la_contrasena(cliente, usuario_registrado, caplog):
    with caplog.at_level(logging.INFO, logger="servidor"):
        cliente.post(
            "/api/auth/inicio-sesion", json={"email": usuario_registrado.email, "contrasena": CONTRASENA}
        )
    assert CONTRASENA not in caplog.text
    assert usuario_registrado.email in caplog.text


def prueba_inicio_sesion_incorrecto_devuelve_401(cliente, usuario_registrado):
    respuesta = cliente.post(
        "/api/auth/inicio-sesion", json={"email": usuario_registrado.email, "contrasena": "incorrecta"}
    )
    assert respuesta.status_code == 401
    assert "sesion" not in cliente.cookies


def prueba_sesion_sin_cookie_devuelve_401(cliente):
    assert cliente.get("/api/auth/sesion").status_code == 401


def prueba_la_sesion_se_mantiene_entre_peticiones(cliente_autenticado, usuario_registrado):
    respuesta = cliente_autenticado.get("/api/auth/sesion")
    assert respuesta.status_code == 200
    assert respuesta.json()["email"] == usuario_registrado.email


def prueba_recuperacion_de_email_desconocido_devuelve_404(cliente):
    assert cliente.post("/api/auth/recuperacion", json={"email": "nadie@ejemplo.com"}).status_code == 404


def prueba_nueva_contrasena_cambia_el_acceso_y_cierra_la_sesion(cliente_autenticado, usuario_registrado):
    respuesta = cliente_autenticado.post("/api/auth/recuperacion", json={"email": usuario_registrado.email})
    assert respuesta.status_code == 200
    token = respuesta.json()["token"]

    assert (
        cliente_autenticado.post(
            "/api/auth/nueva-contrasena", json={"token": token, "contrasena": "nueva-segura"}
        ).status_code
        == 204
    )
    assert cliente_autenticado.get("/api/auth/sesion").status_code == 401
    assert (
        cliente_autenticado.post(
            "/api/auth/inicio-sesion", json={"email": usuario_registrado.email, "contrasena": CONTRASENA}
        ).status_code
        == 401
    )
    assert (
        cliente_autenticado.post(
            "/api/auth/inicio-sesion", json={"email": usuario_registrado.email, "contrasena": "nueva-segura"}
        ).status_code
        == 200
    )


def prueba_nueva_contrasena_queda_guardada_en_el_repositorio(
    cliente, usuario_registrado, repositorio_usuarios, hasher
):
    token = cliente.post("/api/auth/recuperacion", json={"email": usuario_registrado.email}).json()["token"]
    assert cliente.post("/api/auth/nueva-contrasena", json={"token": token, "contrasena": "nueva-segura"}).status_code == 204
    guardado = repositorio_usuarios.obtener_por_email(usuario_registrado.email)
    assert hasher.verificar("nueva-segura", guardado.contrasena_hash)
    assert not hasher.verificar(CONTRASENA, guardado.contrasena_hash)


def prueba_nueva_contrasena_con_token_invalido_devuelve_400(cliente):
    respuesta = cliente.post(
        "/api/auth/nueva-contrasena", json={"token": "no-existe", "contrasena": "nueva-segura"}
    )
    assert respuesta.status_code == 400


def prueba_el_token_de_recuperacion_solo_sirve_una_vez(cliente, usuario_registrado):
    token = cliente.post("/api/auth/recuperacion", json={"email": usuario_registrado.email}).json()["token"]
    assert cliente.post("/api/auth/nueva-contrasena", json={"token": token, "contrasena": "nueva-segura"}).status_code == 204
    assert cliente.post("/api/auth/nueva-contrasena", json={"token": token, "contrasena": "otra-segura"}).status_code == 400


def prueba_cierre_sesion_invalida_el_token(cliente_autenticado):
    token = cliente_autenticado.cookies["sesion"]
    assert cliente_autenticado.post("/api/auth/cierre-sesion").status_code == 204

    cliente_autenticado.cookies.set("sesion", token)
    assert cliente_autenticado.get("/api/auth/sesion").status_code == 401


def _token_confirmacion(enviador_correo):
    return enviador_correo.mensajes[-1][2].split("?confirmar=")[1].split()[0]


def prueba_el_registro_deja_la_cuenta_pendiente_hasta_confirmar(cliente, enviador_correo, repositorio_usuarios):
    assert cliente.post("/api/auth/registro", json=REGISTRO).status_code == 201
    assert enviador_correo.mensajes[0][0] == REGISTRO["email"]
    bloqueada = cliente.post(
        "/api/auth/inicio-sesion",
        json={"email": REGISTRO["email"], "contrasena": REGISTRO["contrasena"]},
    )
    assert bloqueada.status_code == 403
    assert "pendiente" in bloqueada.json()["detail"]

    confirmada = cliente.post("/api/auth/confirmar", json={"token": _token_confirmacion(enviador_correo)})
    assert confirmada.status_code == 200
    assert confirmada.json()["estado"] == "activo"
    assert repositorio_usuarios.obtener_por_email(REGISTRO["email"]).estado.value == "activo"
    assert cliente.post(
        "/api/auth/inicio-sesion",
        json={"email": REGISTRO["email"], "contrasena": REGISTRO["contrasena"]},
    ).status_code == 200


def prueba_un_enlace_de_confirmacion_invalido_devuelve_400(cliente):
    respuesta = cliente.post("/api/auth/confirmar", json={"token": "no-existe"})
    assert respuesta.status_code == 400
    assert "no es válido" in respuesta.json()["detail"]


def prueba_reenviar_confirmacion_invalida_el_enlace_anterior(cliente, enviador_correo):
    assert cliente.post("/api/auth/registro", json=REGISTRO).status_code == 201
    primero = _token_confirmacion(enviador_correo)
    assert cliente.post("/api/auth/reenviar-confirmacion", json={"email": REGISTRO["email"]}).status_code == 204
    assert cliente.post("/api/auth/confirmar", json={"token": primero}).status_code == 400
    assert cliente.post("/api/auth/confirmar", json={"token": _token_confirmacion(enviador_correo)}).status_code == 200


def prueba_no_se_reenvia_la_confirmacion_de_una_cuenta_activa(cliente, usuario_registrado):
    respuesta = cliente.post("/api/auth/reenviar-confirmacion", json={"email": usuario_registrado.email})
    assert respuesta.status_code == 400
    assert "ya está confirmada" in respuesta.json()["detail"]


def prueba_si_el_correo_falla_no_deja_la_cuenta(cliente, repositorio_usuarios):
    from Servidor.aplicacion import aplicacion
    from Servidor.ApiRest.ApiRestDependencies.repositorio_dependencies import obtener_enviador_correo
    from Servidor.Dominio.DominioExceptions.correo_no_enviado import CorreoNoEnviado

    class EnviadorQueFalla:
        def enviar(self, destino, asunto, cuerpo):
            raise CorreoNoEnviado()

    aplicacion.dependency_overrides[obtener_enviador_correo] = lambda: EnviadorQueFalla()
    respuesta = cliente.post("/api/auth/registro", json=REGISTRO)
    assert respuesta.status_code == 502
    assert "correo" in respuesta.json()["detail"]
    assert repositorio_usuarios.obtener_por_email(REGISTRO["email"]) is None


def prueba_google_sin_configurar_avisa(cliente):
    respuesta = cliente.get("/api/auth/google", follow_redirects=False)
    assert respuesta.status_code == 302
    assert respuesta.headers["location"] == "/?aviso=google-no-configurado"


def prueba_google_crea_la_sesion_de_un_usuario_nuevo(cliente, repositorio_usuarios):
    from dataclasses import replace

    from Servidor.aplicacion import aplicacion
    from Servidor.ApiRest.ApiRestDependencies.auth_dependencies import obtener_cliente_google
    from Servidor.ApiRest.ApiRestDependencies.configuracion_dependencies import obtener_configuracion

    class ClienteGoogleFalso:
        def url_autorizacion(self, client_id, redirect_uri, estado):
            return f"https://accounts.google.com/o/oauth2/v2/auth?state={estado}"

        def perfil(self, code, redirect_uri, client_id, client_secret):
            return {"email": "google@ejemplo.com", "name": "Laura Google"}

    config = replace(obtener_configuracion(), google_client_id="cliente", google_client_secret="secreto")
    aplicacion.dependency_overrides[obtener_configuracion] = lambda: config
    aplicacion.dependency_overrides[obtener_cliente_google] = lambda: ClienteGoogleFalso()

    inicio = cliente.get("/api/auth/google", follow_redirects=False)
    assert inicio.status_code == 302
    assert "accounts.google.com" in inicio.headers["location"]
    estado = cliente.cookies["oauth_estado"]
    callback = cliente.get(
        f"/api/auth/google/callback?code=codigo&state={estado}",
        follow_redirects=False,
    )
    assert callback.status_code == 302
    assert callback.headers["location"] == "/"
    assert "sesion" in callback.cookies
    guardado = repositorio_usuarios.obtener_por_email("google@ejemplo.com")
    assert guardado.estado.value == "activo"
    assert guardado.nick == "Laura Google"
    assert cliente.get("/api/auth/sesion").json()["email"] == "google@ejemplo.com"
