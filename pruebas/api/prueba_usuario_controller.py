def prueba_agregar_usuario(cliente):
    respuesta = cliente.post("/api/usuarios", json={"nick": "laura"})
    assert respuesta.status_code == 201
    assert respuesta.json() == {"nick": "laura", "rol": "usuario", "estado": "activo"}


def prueba_agregar_duplicado_devuelve_409(cliente):
    cliente.post("/api/usuarios", json={"nick": "laura"})
    assert cliente.post("/api/usuarios", json={"nick": "laura"}).status_code == 409


def prueba_nick_vacio_devuelve_422(cliente):
    assert cliente.post("/api/usuarios", json={"nick": ""}).status_code == 422


def prueba_listar_y_contar_usuarios(cliente):
    cliente.post("/api/usuarios", json={"nick": "laura"})
    assert len(cliente.get("/api/usuarios").json()) == 1
    assert cliente.get("/api/usuarios/numero").json() == {"numero": 1}


def prueba_usuario_activo(cliente):
    cliente.post("/api/usuarios", json={"nick": "laura"})
    assert cliente.get("/api/usuarios/laura/activo").json() == {"nick": "laura", "activo": True}


def prueba_eliminar_usuario(cliente):
    cliente.post("/api/usuarios", json={"nick": "laura"})
    assert cliente.delete("/api/usuarios/laura").status_code == 204
    assert cliente.delete("/api/usuarios/laura").status_code == 404
