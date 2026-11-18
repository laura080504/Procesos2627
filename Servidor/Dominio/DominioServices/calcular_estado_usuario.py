from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido

PROVEEDORES_VALIDOS = frozenset({"local", "oauth"})
CAMPOS_OBLIGATORIOS = ("proveedor", "confirmado", "eliminado")


def calcular_estado_usuario(datos) -> dict:
    proveedor, confirmado, eliminado = _leer_datos(datos)
    estado = _estado_de(proveedor, confirmado, eliminado)
    return {"estado": estado, "puedeIniciarSesion": estado == "activo"}


def _leer_datos(datos) -> tuple[str, bool, bool]:
    if not isinstance(datos, dict):
        raise EstadoNoValido("El cuerpo debe ser un objeto JSON")

    faltan = [campo for campo in CAMPOS_OBLIGATORIOS if campo not in datos]
    if faltan:
        raise EstadoNoValido("Faltan datos: " + ", ".join(faltan))

    proveedor = datos["proveedor"]
    confirmado = datos["confirmado"]
    eliminado = datos["eliminado"]

    if not isinstance(confirmado, bool) or not isinstance(eliminado, bool):
        raise EstadoNoValido("confirmado y eliminado deben ser booleanos")
    if proveedor not in PROVEEDORES_VALIDOS:
        raise EstadoNoValido("El proveedor debe ser local u oauth")
    return proveedor, confirmado, eliminado


def _estado_de(proveedor: str, confirmado: bool, eliminado: bool) -> str:
    # eliminado > activo (oauth o local confirmado) > pendiente (local sin confirmar)
    if eliminado:
        return "eliminado"
    if proveedor == "oauth" or confirmado:
        return "activo"
    return "pendiente"
