def prueba_variante6_el_ejemplo_del_contrato(cliente):
    respuesta = cliente.post(
        "/api/prueba/estado",
        json={"proveedor": "local", "confirmado": False, "eliminado": False},
    )
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "pendiente", "puedeIniciarSesion": False}


def prueba_variante6_rechaza_proveedor_desconocido_en_la_api(cliente):
    respuesta = cliente.post(
        "/api/prueba/estado",
        json={"proveedor": "google", "confirmado": False, "eliminado": False},
    )
    assert respuesta.status_code == 400
    assert "error" in respuesta.json()


def prueba_variante6_rechaza_datos_ausentes(cliente):
    respuesta = cliente.post("/api/prueba/estado", json={"proveedor": "local"})
    assert respuesta.status_code == 400
    assert "error" in respuesta.json()


def prueba_variante6_no_pide_sesion(cliente):
    assert "sesion" not in cliente.cookies
    respuesta = cliente.post(
        "/api/prueba/estado",
        json={"proveedor": "local", "confirmado": True, "eliminado": False},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["puedeIniciarSesion"] is True
