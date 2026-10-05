def prueba_rutas_de_usuarios_rechazan_peticiones_sin_sesion(cliente, usuario_registrado):
    assert cliente.get("/api/usuarios").status_code == 401
    assert cliente.get("/api/usuarios/numero").status_code == 401
    assert cliente.get(f"/api/usuarios/{usuario_registrado.email}/activo").status_code == 401
    assert cliente.delete(f"/api/usuarios/{usuario_registrado.email}").status_code == 401


def prueba_listar_usuarios(cliente_autenticado, usuario_registrado):
    respuesta = cliente_autenticado.get("/api/usuarios")
    assert respuesta.status_code == 200
    assert respuesta.json() == [
        {"email": usuario_registrado.email, "nick": "laura", "rol": "usuario", "estado": "activo"}
    ]


def prueba_numero_usuarios(cliente_autenticado):
    assert cliente_autenticado.get("/api/usuarios/numero").json() == {"numero": 1}


def prueba_usuario_activo(cliente_autenticado, usuario_registrado):
    respuesta = cliente_autenticado.get(f"/api/usuarios/{usuario_registrado.email}/activo")
    assert respuesta.json() == {"email": usuario_registrado.email, "activo": True}


def prueba_eliminar_usuario_inexistente_devuelve_404(cliente_autenticado):
    assert cliente_autenticado.delete("/api/usuarios/nadie@ejemplo.com").status_code == 404


def prueba_eliminar_usuario_cierra_sus_sesiones(cliente_autenticado, usuario_registrado):
    assert cliente_autenticado.delete(f"/api/usuarios/{usuario_registrado.email}").status_code == 204
    assert cliente_autenticado.get("/api/auth/sesion").status_code == 401
