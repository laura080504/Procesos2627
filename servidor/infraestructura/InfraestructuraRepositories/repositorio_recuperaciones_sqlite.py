from __future__ import annotations

import sqlite3
from datetime import datetime

from Servidor.Infraestructura.base_datos_sqlite import BaseDatosSqlite
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones import RepositorioRecuperaciones
from Servidor.Dominio.DominioEntities.recuperacion import Recuperacion


class RepositorioRecuperacionesSqlite(RepositorioRecuperaciones):
    def __init__(self, base_datos: BaseDatosSqlite):
        self.base_datos = base_datos

    def guardar(self, recuperacion: Recuperacion) -> Recuperacion:
        with self.base_datos.conectar() as conexion:
            conexion.execute(
                """
                INSERT INTO recuperaciones (token, email, expira_en)
                VALUES (?, ?, ?)
                ON CONFLICT(token) DO UPDATE SET email = excluded.email, expira_en = excluded.expira_en
                """,
                (recuperacion.token, recuperacion.email, recuperacion.expira_en.isoformat()),
            )
        return recuperacion

    def obtener(self, token: str) -> Recuperacion | None:
        with self.base_datos.conectar() as conexion:
            fila = conexion.execute("SELECT * FROM recuperaciones WHERE token = ?", (token,)).fetchone()
        return self._a_recuperacion(fila) if fila else None

    def eliminar(self, token: str) -> None:
        with self.base_datos.conectar() as conexion:
            conexion.execute("DELETE FROM recuperaciones WHERE token = ?", (token,))

    def eliminar_por_email(self, email: str) -> None:
        with self.base_datos.conectar() as conexion:
            conexion.execute("DELETE FROM recuperaciones WHERE email = ?", (email,))

    def _a_recuperacion(self, fila: sqlite3.Row) -> Recuperacion:
        return Recuperacion(
            token=fila["token"], email=fila["email"], expira_en=datetime.fromisoformat(fila["expira_en"])
        )
