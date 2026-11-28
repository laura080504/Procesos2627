from __future__ import annotations

from datetime import date, datetime

from Servidor.Dominio.DominioEntities.aviso_secretaria import AvisoSecretaria
from Servidor.Dominio.DominioEnums.tipo_aviso_secretaria import TipoAvisoSecretaria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_avisos_secretaria import (
    RepositorioAvisosSecretaria,
)
from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo


class RepositorioAvisosSecretariaMongo(RepositorioAvisosSecretaria):
    def __init__(self, base_datos: BaseDatosMongo):
        self.base_datos = base_datos
        self._coleccion = base_datos.coleccion("avisos_secretaria")

    def obtener_todos(self) -> list[AvisoSecretaria]:
        return [self._desde_documento(documento) for documento in self._coleccion.find()]

    def obtener_por_id(self, aviso_id: str) -> AvisoSecretaria | None:
        documento = self._coleccion.find_one({"_id": aviso_id})
        if documento is None:
            return None
        return self._desde_documento(documento)

    def guardar(self, aviso: AvisoSecretaria) -> AvisoSecretaria:
        con_id = aviso.con_id()
        assert con_id.id is not None
        self._coleccion.replace_one(
            {"_id": con_id.id},
            {
                "_id": con_id.id,
                "titulo": con_id.titulo,
                "tipo": con_id.tipo.value,
                "fecha": con_id.fecha.isoformat(),
                "hora": con_id.hora,
                "lugar": con_id.lugar,
                "url": con_id.url,
                "descripcion": con_id.descripcion,
            },
            upsert=True,
        )
        return con_id

    def eliminar(self, aviso_id: str) -> bool:
        return self._coleccion.delete_one({"_id": aviso_id}).deleted_count > 0

    def vacio(self) -> bool:
        return self._coleccion.estimated_document_count() == 0

    def _desde_documento(self, documento: dict) -> AvisoSecretaria:
        fecha = documento["fecha"]
        if isinstance(fecha, datetime):
            fecha = fecha.date()
        elif isinstance(fecha, str):
            fecha = date.fromisoformat(fecha)
        return AvisoSecretaria(
            titulo=documento["titulo"],
            tipo=TipoAvisoSecretaria(documento["tipo"]),
            fecha=fecha,
            hora=documento.get("hora") or "00:00",
            lugar=documento.get("lugar"),
            url=documento.get("url"),
            descripcion=documento.get("descripcion"),
            id=documento["_id"],
        )
