"""Docencia de demostración: admin@gmail.com ≈ GALLUD en Procesos y Diseño."""

from __future__ import annotations

from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia import RepositorioDocencia
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios

EMAIL_GALLUD = "admin@gmail.com"
NOMBRE_GALLUD = "GALLUD LAZARO, JOSE ANTONIO"
# Procesos de Ingeniería del Software (1.er cuatri) + Diseño de Software (2.º cuatri).
CODIGOS_GALLUD = ("42330", "42327")


def asegurar_docencia_muestra(repositorio: RepositorioDocencia) -> None:
    """Siembra la docencia de Gallud solo si ese correo aún no tiene asignaturas."""
    email = EMAIL_GALLUD
    if repositorio.obtener_codigos(email):
        if not repositorio.obtener_nombre_docente(email):
            repositorio.reemplazar(email, repositorio.obtener_codigos(email), NOMBRE_GALLUD)
        return
    repositorio.reemplazar(email, list(CODIGOS_GALLUD), NOMBRE_GALLUD)


def asegurar_rol_profesor_gallud(repositorio_usuarios: RepositorioUsuarios) -> None:
    """admin@gmail.com es profesor (admin), nunca secretaría/superadmin."""
    usuario = repositorio_usuarios.obtener_por_email(EMAIL_GALLUD)
    if usuario is None or usuario.rol == Rol.PROFESOR:
        return
    usuario.rol = Rol.PROFESOR
    repositorio_usuarios.actualizar(usuario)
