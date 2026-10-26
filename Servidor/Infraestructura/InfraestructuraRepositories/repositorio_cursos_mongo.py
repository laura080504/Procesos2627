from __future__ import annotations

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos import RepositorioCursos


class RepositorioCursosMongo(RepositorioCursos):
    def __init__(self, base_datos: BaseDatosMongo):
        self.base_datos = base_datos

    def obtener(self, curso: str) -> list[Asignatura]:
        documentos = self.base_datos.coleccion(curso).find().sort("_id", 1)
        return [self._a_asignatura(documento) for documento in documentos]

    def guardar(self, asignatura: Asignatura) -> None:
        self.base_datos.coleccion(asignatura.curso.value).update_one(
            {"_id": asignatura.codigo},
            {"$set": self._a_documento(asignatura)},
            upsert=True,
        )

    def _a_documento(self, asignatura: Asignatura) -> dict:
        return {
            "nombre": asignatura.nombre,
            "nombre_ingles": asignatura.nombre_ingles,
            "curso": asignatura.curso.value,
            "creditos": asignatura.creditos,
            "cuatrimestre": asignatura.cuatrimestre,
        }

    def _a_asignatura(self, documento: dict) -> Asignatura:
        return Asignatura(
            codigo=documento["_id"],
            nombre=documento["nombre"],
            nombre_ingles=documento["nombre_ingles"],
            curso=CursoAsignatura(documento["curso"]),
            creditos=documento["creditos"],
            cuatrimestre=documento["cuatrimestre"],
        )
