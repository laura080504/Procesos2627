import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioServices.calcular_estado_usuario import calcular_estado_usuario

router = APIRouter(prefix="/api/prueba", tags=["prueba"])


@router.post("/estado")
async def estado(request: Request):
    try:
        datos = await request.json()
        return calcular_estado_usuario(datos)
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "El cuerpo debe ser JSON"})
    except EstadoNoValido as error:
        return JSONResponse(status_code=400, content={"error": str(error)})
