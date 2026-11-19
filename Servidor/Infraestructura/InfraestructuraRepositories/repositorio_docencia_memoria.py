from __future__ import annotations

from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia import RepositorioDocencia


class RepositorioDocenciaMemoria(RepositorioDocencia):
    def __init__(self):
        self._codigos: dict[str, list[str]] = {}
        self._nombres: dict[str, str] = {}

    def obtener_codigos(self, email: str) -> list[str]:
        return list(self._codigos.get(email.strip().lower(), []))

    def obtener_nombre_docente(self, email: str) -> str | None:
        return self._nombres.get(email.strip().lower())

    def reemplazar(
        self,
        email: str,
        codigos: list[str],
        nombre_docente: str | None = None,
    ) -> None:
        clave = email.strip().lower()
        self._codigos[clave] = list(dict.fromkeys(codigo.strip() for codigo in codigos if codigo.strip()))
        if nombre_docente is not None:
            nombre = nombre_docente.strip()
            if nombre:
                self._nombres[clave] = nombre
            else:
                self._nombres.pop(clave, None)
