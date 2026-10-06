def prueba_sirve_el_cliente(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert "Procesos 26-27" in respuesta.text
