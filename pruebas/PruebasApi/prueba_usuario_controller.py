def prueba_rutas_de_usuarios_rechazan_peticiones_sin_sesion(cliente, usuario_registrado):
    assert cliente.get("/api/usuarios").status_code == 401
    assert cliente.get("/api/usuarios/numero").status_code == 401
    assert cliente.get(f"/api/usuarios/{usuario_registrado.email}/activo").status_code == 401
    assert cliente.delete(f"/api/usuarios/{usuario_registrado.email}").status_code == 401


def prueba_un_usuario_no_lista_usuarios(cliente_autenticado):
    assert cliente_autenticado.get("/api/usuarios").status_code == 403
    assert cliente_autenticado.get("/api/usuarios/numero").status_code == 403
    assert cliente_autenticado.get("/api/usuarios/laura@ejemplo.com/activo").status_code == 403


def prueba_un_administrador_lista_usuarios(cliente_administrador, usuario_registrado, administrador):
    respuesta = cliente_administrador.get("/api/usuarios")
    assert respuesta.status_code == 200
    assert {usuario["email"] for usuario in respuesta.json()} == {usuario_registrado.email, administrador.email}
    assert cliente_administrador.get("/api/usuarios/numero").json() == {"numero": 2}
    activo = cliente_administrador.get(f"/api/usuarios/{usuario_registrado.email}/activo")
    assert activo.json() == {"email": usuario_registrado.email, "activo": True}


def prueba_un_usuario_no_elimina_a_otro(cliente_autenticado, administrador, repositorio_usuarios):
    assert cliente_autenticado.delete(f"/api/usuarios/{administrador.email}").status_code == 403
    assert repositorio_usuarios.obtener_por_email(administrador.email) is not None


def prueba_un_administrador_elimina_a_otro(cliente_administrador, usuario_registrado, repositorio_usuarios):
    assert cliente_administrador.delete(f"/api/usuarios/{usuario_registrado.email}").status_code == 204
    assert repositorio_usuarios.obtener_por_email(usuario_registrado.email) is None


def prueba_eliminar_usuario_inexistente_devuelve_404(cliente_administrador):
    assert cliente_administrador.delete("/api/usuarios/nadie@ejemplo.com").status_code == 404


def prueba_eliminar_usuario_cierra_sus_sesiones(cliente_autenticado, usuario_registrado):
    assert cliente_autenticado.delete(f"/api/usuarios/{usuario_registrado.email}").status_code == 204
    assert cliente_autenticado.get("/api/auth/sesion").status_code == 401
