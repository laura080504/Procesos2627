import queue
import threading

import pytest
from starlette.websockets import WebSocketDisconnect


def prueba_websocket_sin_sesion_no_conecta(cliente):
    with pytest.raises(WebSocketDisconnect):
        with cliente.websocket_connect("/ws") as conexion:
            conexion.receive_text()


def prueba_websocket_no_reenvia_lo_que_envia_el_cliente(cliente, usuario_registrado):
    from Pruebas.conftest import CONTRASENA

    assert cliente.post(
        "/api/auth/inicio-sesion",
        json={"email": usuario_registrado.email, "contrasena": CONTRASENA},
    ).status_code == 200
    with cliente.websocket_connect("/ws") as conexion:
        conexion.send_json({"tipo": "evento_nuevo", "codigo": "42330", "nombre": "Falso"})
        recibidos = queue.Queue()

        def leer():
            try:
                recibidos.put(conexion.receive_json())
            except Exception as error:
                recibidos.put(error)

        hilo = threading.Thread(target=leer, daemon=True)
        hilo.start()
        hilo.join(0.4)
        assert recibidos.empty()
