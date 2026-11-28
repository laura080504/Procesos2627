from __future__ import annotations

from datetime import date

from Servidor.Dominio.DominioEntities.evento import Evento, identidad_evento
from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento
from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos


class RepositorioEventosMongo(RepositorioEventos):
    def __init__(self, base_datos: BaseDatosMongo):
        self.base_datos = base_datos

    def obtener_todos(self) -> list[Evento]:
        documentos = self.base_datos.coleccion("evento").find()
        return [self._a_evento(documento) for documento in documentos]

    def obtener_por_id(self, evento_id: str) -> Evento | None:
        documento = self.base_datos.coleccion("evento").find_one({"_id": evento_id})
        if documento is None:
            return None
        return self._a_evento(documento)

    def reemplazar(self, eventos: list[Evento]) -> None:
        coleccion = self.base_datos.coleccion("evento")
        coleccion.delete_many({})
        if eventos:
            coleccion.insert_many(
                [{"_id": identidad_evento(evento.con_id()), **self._a_documento(evento.con_id())} for evento in eventos]
            )

    def guardar(self, evento: Evento) -> None:
        con_id = evento.con_id()
        clave = identidad_evento(con_id)
        coleccion = self.base_datos.coleccion("evento")
        coleccion.replace_one(
            {"_id": clave},
            {"_id": clave, **self._a_documento(con_id)},
            upsert=True,
        )

    def eliminar(self, evento_id: str) -> bool:
        resultado = self.base_datos.coleccion("evento").delete_one({"_id": evento_id})
        return resultado.deleted_count > 0

    def _a_documento(self, evento: Evento) -> dict:
        return {
            "id": identidad_evento(evento),
            "fecha": evento.fecha.isoformat(),
            "codigo": evento.codigo,
            "tipo": evento.tipo.value,
            "hora": evento.hora,
            "lugar": evento.lugar,
        }

    def _a_evento(self, documento: dict) -> Evento:
        tipo = TipoEvento(documento["tipo"])
        codigo = documento["codigo"]
        lugar = None
        if tipo == TipoEvento.EXAMEN:
            lugar = documento.get("lugar") or _aula_por_defecto(codigo)
        evento_id = documento.get("id") or str(documento.get("_id") or "")
        return Evento(
            fecha=date.fromisoformat(documento["fecha"]),
            codigo=codigo,
            tipo=tipo,
            hora=documento.get("hora") or _hora_por_defecto(codigo, tipo),
            lugar=lugar,
            id=evento_id or None,
        )


def _hora_por_defecto(codigo: str, tipo: TipoEvento) -> str:
    base = sum(ord(caracter) for caracter in codigo) % 4
    if tipo == TipoEvento.EXAMEN:
        return ("09:00", "11:30", "16:00", "18:00")[base]
    return ("12:00", "14:00", "18:00", "23:59")[base]


def _aula_por_defecto(codigo: str) -> str:
    base = int(codigo[-2:]) if codigo[-2:].isdigit() else 1
    return f"Aula {(base % 3) + 1}.{(base % 4) + 1}"
