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


def prueba_las_marcas_llegan_con_estrellas_delante(cliente_autenticado):
    respuesta = cliente_autenticado.get("/api/agenda/marcas", params={"anio": 2026, "mes": 10})
    assert respuesta.status_code == 200
    marcas = {marca["dia"]: [simbolo["tipo"] for simbolo in marca["simbolos"]] for marca in respuesta.json()}
    assert marcas[11] == ["estrella"] * 5
    assert marcas[16] == ["estrella", "estrella", "punto"]
    assert marcas[27] == ["estrella", "punto", "punto"]
    simbolo = respuesta.json()[0]["simbolos"][0]
    assert simbolo["codigo"]
    assert simbolo["hora"]
    assert "lugar" in simbolo
