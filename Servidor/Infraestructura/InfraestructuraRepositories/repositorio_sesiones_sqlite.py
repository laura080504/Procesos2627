from __future__ import annotations

import sqlite3
from datetime import datetime

from Servidor.Infraestructura.base_datos_sqlite import BaseDatosSqlite
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Dominio.DominioEntities.sesion import Sesion


class RepositorioSesionesSqlite(RepositorioSesiones):
    def __init__(self, base_datos: BaseDatosSqlite):
        self.base_datos = base_datos

    def guardar(self, sesion: Sesion) -> Sesion:
        with self.base_datos.conectar() as conexion:
            conexion.execute(
                """
                INSERT INTO sesiones (token, email, expira_en)
                VALUES (?, ?, ?)
                ON CONFLICT(token) DO UPDATE SET email = excluded.email, expira_en = excluded.expira_en
                """,
                (sesion.token, sesion.email, sesion.expira_en.isoformat()),
            )
        return sesion

    def obtener(self, token: str) -> Sesion | None:
        with self.base_datos.conectar() as conexion:
            fila = conexion.execute("SELECT * FROM sesiones WHERE token = ?", (token,)).fetchone()
        return self._a_sesion(fila) if fila else None

    def eliminar(self, token: str) -> None:
        with self.base_datos.conectar() as conexion:
            conexion.execute("DELETE FROM sesiones WHERE token = ?", (token,))

    def eliminar_por_email(self, email: str) -> None:
        with self.base_datos.conectar() as conexion:
            conexion.execute("DELETE FROM sesiones WHERE email = ?", (email,))

    def _a_sesion(self, fila: sqlite3.Row) -> Sesion:
        return Sesion(token=fila["token"], email=fila["email"], expira_en=datetime.fromisoformat(fila["expira_en"]))
