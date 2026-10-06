from __future__ import annotations

import re
import sqlite3
from pathlib import Path


class MigradorSqlite:
    _patron = re.compile(r"^\d{3}_[a-z0-9_]+\.sql$")

    def __init__(self, ruta: Path, carpeta: Path | None = None):
        self.ruta = Path(ruta)
        self.carpeta = Path(carpeta) if carpeta else Path(__file__).resolve().parent / "versiones"

    def aplicar(self) -> list[str]:
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        aplicadas = []
        with sqlite3.connect(self.ruta) as conexion:
            conexion.execute("DROP TABLE IF EXISTS esquema_migraciones")
            version = conexion.execute("PRAGMA user_version").fetchone()[0]
            for archivo in self._archivos():
                numero = int(archivo.name[:3])
                if numero <= version:
                    continue
                if numero != version + 1:
                    raise ValueError(
                        f"La migracion {archivo.name} no encadena con la {version:03d}. "
                        f"La siguiente tiene que ser {version + 1:03d}."
                    )
                for sentencia in self._sentencias(archivo.read_text(encoding="utf-8")):
                    conexion.execute(sentencia)
                conexion.execute(f"PRAGMA user_version = {numero}")
                version = numero
                aplicadas.append(archivo.stem)
        return aplicadas

    def _archivos(self) -> list[Path]:
        archivos = [archivo for archivo in self.carpeta.glob("*.sql") if self._patron.fullmatch(archivo.name)]
        return sorted(archivos, key=lambda archivo: archivo.name)

    def _sentencias(self, sql: str) -> list[str]:
        lineas = [linea for linea in sql.splitlines() if not linea.strip().startswith("--")]
        return [sentencia.strip() for sentencia in "\n".join(lineas).split(";") if sentencia.strip()]
