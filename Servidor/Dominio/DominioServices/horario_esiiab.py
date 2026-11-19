"""Acceso al horario vivo de la ESIIAB.

Las franjas salen de https://esiiab.uclm.es/horarios/ a través del cliente de
infraestructura: todos los cursos, grupos (A/B/C/I) e intensificaciones.
El aula cuenta como teoría y el laboratorio (SOFTW, HW, Elect o Lab) como
prácticas. Cada sesión lleva la etiqueta de su grupo.
"""

from __future__ import annotations

from collections.abc import Callable

from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto
from Servidor.Dominio.DominioServices.parser_horarios_esiiab import Sesion

ProveedorSesiones = Callable[[], dict[str, tuple[Sesion, ...]]]

_proveedor_sesiones: ProveedorSesiones | None = None


def configurar_proveedor_sesiones(proveedor: ProveedorSesiones | None) -> None:
    """Enlaza el cliente vivo de la ESIIAB. None deja el horario vacío."""
    global _proveedor_sesiones
    _proveedor_sesiones = proveedor


def mapa_sesiones() -> dict[str, tuple[Sesion, ...]]:
    """Una sola lectura del proveedor para no repetir sync por asignatura."""
    if _proveedor_sesiones is None:
        return {}
    try:
        return _proveedor_sesiones() or {}
    except Exception:
        return {}


def sesiones_de(nombre: str) -> tuple[Sesion, ...]:
    return mapa_sesiones().get(normalizar_texto(nombre), ())
