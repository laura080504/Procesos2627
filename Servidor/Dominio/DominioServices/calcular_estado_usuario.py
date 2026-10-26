from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido

PROVEEDORES = {"local", "oauth"}


def calcular_estado_usuario(datos) -> dict:
    if not isinstance(datos, dict):
        raise EstadoNoValido("El cuerpo debe ser un objeto JSON")
    faltan = [campo for campo in ("proveedor", "confirmado", "eliminado") if campo not in datos]
    if faltan:
        raise EstadoNoValido("Faltan datos: " + ", ".join(faltan))
    proveedor = datos["proveedor"]
    confirmado = datos["confirmado"]
    eliminado = datos["eliminado"]
    if type(confirmado) is not bool or type(eliminado) is not bool:
        raise EstadoNoValido("confirmado y eliminado deben ser booleanos")
    if proveedor not in PROVEEDORES:
        raise EstadoNoValido("El proveedor debe ser local u oauth")
    if eliminado:
        estado = "eliminado"
    elif proveedor == "oauth" or confirmado:
        estado = "activo"
    else:
        estado = "pendiente"
    return {"estado": estado, "puedeIniciarSesion": estado == "activo"}
