def prueba_websocket_difunde_mensajes(cliente):
    with cliente.websocket_connect("/ws") as conexion:
        conexion.send_json({"tipo": "hola"})
        assert conexion.receive_json() == {"tipo": "hola"}
