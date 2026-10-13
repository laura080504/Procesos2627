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
        "estado": "activo",
    }


def prueba_registro_guarda_el_usuario_en_el_repositorio(cliente, repositorio_usuarios):
    assert cliente.post("/api/auth/registro", json=REGISTRO).status_code == 201
    guardado = repositorio_usuarios.obtener_por_email(REGISTRO["email"])
    assert guardado is not None
    assert guardado.nick == REGISTRO["nick"]
    assert guardado.rol.value == "usuario"
    assert guardado.estado.value == "activo"
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
