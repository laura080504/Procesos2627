from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from servidor.infraestructura.migraciones.migrador_sqlite import MigradorSqlite


class BaseDatosSqlite:
    def __init__(self, ruta: str | Path):
        archivo = Path(ruta)
        if not archivo.is_absolute():
            archivo = Path(__file__).resolve().parents[2] / archivo
        archivo.parent.mkdir(parents=True, exist_ok=True)
        self.ruta = archivo
        MigradorSqlite(self.ruta).aplicar()

    @contextmanager
    def conectar(self) -> Iterator[sqlite3.Connection]:
        conexion = sqlite3.connect(self.ruta)
        conexion.row_factory = sqlite3.Row
        try:
            yield conexion
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()
