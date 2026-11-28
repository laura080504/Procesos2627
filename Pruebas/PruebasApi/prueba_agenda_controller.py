def prueba_la_agenda_exige_sesion(cliente):
    assert cliente.get("/api/asignaturas").status_code == 401
    assert cliente.get("/api/agenda/marcas").status_code == 401
    assert cliente.get("/api/matricula").status_code == 401


def prueba_un_usuario_lista_y_busca_asignaturas(cliente_autenticado):
    todas = cliente_autenticado.get("/api/asignaturas")
    assert todas.status_code == 200
    codigos = {asignatura["codigo"] for asignatura in todas.json()}
    assert {"42300", "42319", "42330", "42358"} <= codigos
    busqueda = cliente_autenticado.get("/api/asignaturas", params={"nombre": "calculo"})
    assert [asignatura["codigo"] for asignatura in busqueda.json()] == ["42300"]
    assert busqueda.json()[0]["curso"] == "primero"


def prueba_las_marcas_no_traen_semilla_ficticia(cliente_autenticado):
    respuesta = cliente_autenticado.get("/api/agenda/marcas", params={"anio": 2026, "mes": 11})
    assert respuesta.status_code == 200
    simbolos = [simbolo for marca in respuesta.json() for simbolo in marca["simbolos"]]
    inventados = [
        simbolo
        for simbolo in simbolos
        if simbolo["tipo"] in ("estrella", "punto")
        and simbolo.get("codigo") in {"42300", "42304", "42302", "42314"}
        and simbolo.get("fecha", "").startswith("2026-11-")
    ]
    assert inventados == []
    # Pueden quedar marcas oficiales del calendario académico (festivo, periodo…).
    for simbolo in simbolos:
        assert simbolo["tipo"]
        assert simbolo["fecha"]


def prueba_un_usuario_sin_matricula_empieza_vacio(cliente_autenticado):
    respuesta = cliente_autenticado.get("/api/matricula")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["asignaturas"] == []
    assert cuerpo["horario"] == []
    assert cuerpo["creditos_aprobados"] == 0
    assert cuerpo["creditos_convalidados"] == 0


def prueba_profesor_publica_evento_y_aparece_en_marcas(
    cliente, administrador, usuario_registrado, repositorio_docencia
):
    from Pruebas.conftest import CONTRASENA

    repositorio_docencia.reemplazar(administrador.email, ["42302"])
    assert cliente.post(
        "/api/auth/inicio-sesion",
        json={"email": administrador.email, "contrasena": CONTRASENA},
    ).status_code == 200
    creado = cliente.post(
        "/api/eventos",
        json={
            "codigo": "42302",
            "tipo": "entrega",
            "fecha": "2026-12-15",
            "hora": "23:59",
            "lugar": None,
        },
    )
    assert creado.status_code == 201
    assert creado.json()["fecha"] == "2026-12-15"
    assert creado.json()["hora"] == "23:59"

    assert cliente.post(
        "/api/auth/inicio-sesion",
        json={"email": usuario_registrado.email, "contrasena": CONTRASENA},
    ).status_code == 200
    marcas = cliente.get("/api/agenda/marcas", params={"anio": 2026, "mes": 12})
    assert marcas.status_code == 200
    del_15 = next(marca for marca in marcas.json() if marca["dia"] == 15)
    simbolo = next(item for item in del_15["simbolos"] if item["codigo"] == "42302" and item["hora"] == "23:59")
    assert simbolo["tipo"] == "punto"
    assert simbolo["fecha"] == "2026-12-15"


def prueba_alumno_no_puede_publicar_evento(cliente_autenticado):
    respuesta = cliente_autenticado.post(
        "/api/eventos",
        json={
            "codigo": "42302",
            "tipo": "examen",
            "fecha": "2026-12-16",
            "hora": "09:00",
            "lugar": "Aula 1",
        },
    )
    assert respuesta.status_code == 403


def prueba_profesor_no_publica_evento_en_asignatura_ajena(cliente_administrador, repositorio_docencia):
    repositorio_docencia.reemplazar("admin@ejemplo.com", ["42330"])
    respuesta = cliente_administrador.post(
        "/api/eventos",
        json={
            "codigo": "42302",
            "tipo": "entrega",
            "fecha": "2026-12-17",
            "hora": "23:59",
            "lugar": None,
        },
    )
    assert respuesta.status_code == 403


def prueba_el_aviso_llega_al_alumno_matriculado(
    cliente, usuario_registrado, administrador, repositorio_docencia, repositorio_matriculas
):
    from Pruebas.conftest import CONTRASENA

    repositorio_docencia.reemplazar(administrador.email, ["42330"])
    repositorio_matriculas.reemplazar_alumno(usuario_registrado.email, ["42330"])
    assert cliente.post(
        "/api/auth/inicio-sesion",
        json={"email": usuario_registrado.email, "contrasena": CONTRASENA},
    ).status_code == 200
    cookies_alumno = dict(cliente.cookies)

    with cliente.websocket_connect("/ws", cookies=cookies_alumno) as socket:
        assert cliente.post(
            "/api/auth/inicio-sesion",
            json={"email": administrador.email, "contrasena": CONTRASENA},
        ).status_code == 200
        creado = cliente.post(
            "/api/eventos",
            json={
                "codigo": "42330",
                "tipo": "entrega",
                "fecha": "2026-12-20",
                "hora": "23:59",
                "lugar": None,
            },
        )
        assert creado.status_code == 201
        mensaje = socket.receive_json()

    assert mensaje["tipo"] == "evento_nuevo"
    assert mensaje["codigo"] == "42330"
    assert mensaje["fecha"] == "2026-12-20"


def prueba_profesor_edita_y_elimina_evento(cliente, administrador, repositorio_docencia):
    from Pruebas.conftest import CONTRASENA

    repositorio_docencia.reemplazar(administrador.email, ["42302"])
    assert cliente.post(
        "/api/auth/inicio-sesion",
        json={"email": administrador.email, "contrasena": CONTRASENA},
    ).status_code == 200
    creado = cliente.post(
        "/api/eventos",
        json={
            "codigo": "42302",
            "tipo": "examen",
            "fecha": "2026-12-18",
            "hora": "09:00",
            "lugar": "Aula 1.1",
        },
    )
    assert creado.status_code == 201
    evento_id = creado.json()["id"]
    assert evento_id

    editado = cliente.put(
        f"/api/eventos/{evento_id}",
        json={
            "codigo": "42302",
            "tipo": "entrega",
            "fecha": "2026-12-19",
            "hora": "23:59",
            "lugar": None,
        },
    )
    assert editado.status_code == 200
    assert editado.json()["id"] == evento_id
    assert editado.json()["tipo"] == "entrega"
    assert editado.json()["fecha"] == "2026-12-19"

    marcas = cliente.get("/api/agenda/marcas", params={"anio": 2026, "mes": 12})
    del_19 = next(marca for marca in marcas.json() if marca["dia"] == 19)
    simbolo = next(item for item in del_19["simbolos"] if item.get("evento_id") == evento_id)
    assert simbolo["editable"] is True
    assert simbolo["tipo"] == "punto"

    borrado = cliente.delete(f"/api/eventos/{evento_id}")
    assert borrado.status_code == 204
    marcas_tras = cliente.get("/api/agenda/marcas", params={"anio": 2026, "mes": 12})
    ids = [
        item.get("evento_id")
        for marca in marcas_tras.json()
        for item in marca["simbolos"]
    ]
    assert evento_id not in ids
