from __future__ import annotations

import sqlite3

from servidor.infraestructura.base_datos_sqlite import BaseDatosSqlite
from servidor.infraestructura.repositories.repositorio_usuarios import RepositorioUsuarios
from servidor.dominio.entities.usuario import Usuario
from servidor.dominio.enums.estado_usuario import EstadoUsuario
from servidor.dominio.enums.rol import Rol


class RepositorioUsuariosSqlite(RepositorioUsuarios):
    def __init__(self, base_datos: BaseDatosSqlite):
        self.base_datos = base_datos

    def insertar(self, usuario: Usuario) -> Usuario:
        with self.base_datos.conectar() as conexion:
            conexion.execute(
                """
                INSERT INTO usuarios (email, nick, contrasena_hash, rol, estado)
                VALUES (?, ?, ?, ?, ?)
                """,
                (usuario.email, usuario.nick, usuario.contrasena_hash, usuario.rol.value, usuario.estado.value),
            )
        return usuario

    def obtener_por_email(self, email: str) -> Usuario | None:
        with self.base_datos.conectar() as conexion:
            fila = conexion.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
        return self._a_usuario(fila) if fila else None

    def obtener_todos(self) -> list[Usuario]:
        with self.base_datos.conectar() as conexion:
            filas = conexion.execute("SELECT * FROM usuarios ORDER BY email").fetchall()
        return [self._a_usuario(fila) for fila in filas]

    def actualizar(self, usuario: Usuario) -> None:
        with self.base_datos.conectar() as conexion:
            conexion.execute(
                """
                UPDATE usuarios
                SET nick = ?, contrasena_hash = ?, rol = ?, estado = ?
                WHERE email = ?
                """,
                (usuario.nick, usuario.contrasena_hash, usuario.rol.value, usuario.estado.value, usuario.email),
            )

    def eliminar(self, email: str) -> bool:
        with self.base_datos.conectar() as conexion:
            cursor = conexion.execute("DELETE FROM usuarios WHERE email = ?", (email,))
            return cursor.rowcount > 0

    def _a_usuario(self, fila: sqlite3.Row) -> Usuario:
        return Usuario(
            email=fila["email"],
            nick=fila["nick"],
            contrasena_hash=fila["contrasena_hash"],
            rol=Rol(fila["rol"]),
            estado=EstadoUsuario(fila["estado"]),
        )
