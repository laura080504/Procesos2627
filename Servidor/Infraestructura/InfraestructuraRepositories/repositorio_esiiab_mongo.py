from __future__ import annotations

from datetime import datetime, timezone

from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto
from Servidor.Dominio.DominioServices.parser_ficha_esiiab import FichaEsiiab, ProfesorEsiiab
from Servidor.Dominio.DominioServices.parser_horarios_esiiab import HorarioPublicoEsiiab, Sesion
from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_esiiab import RepositorioEsiiab


class RepositorioEsiiabMongo(RepositorioEsiiab):
    def __init__(self, base_datos: BaseDatosMongo):
        self.base_datos = base_datos

    def guardar_horario(self, horario: HorarioPublicoEsiiab, sincronizado_en: datetime | None = None) -> None:
        momento = sincronizado_en or datetime.now(timezone.utc)
        sesiones = self.base_datos.coleccion("esiiab_sesiones")
        meta = self.base_datos.coleccion("esiiab_meta")
        documentos = []
        for nombre, franjas in horario.sesiones.items():
            for dia, inicio, fin, tipo, aula, grupo in franjas:
                documentos.append(
                    {
                        "_id": f"{nombre}|{grupo}|{dia}|{inicio}|{fin}|{tipo}|{aula}",
                        "nombre_normalizado": nombre,
                        "grupo": grupo,
                        "dia": dia,
                        "inicio": inicio,
                        "fin": fin,
                        "tipo": tipo,
                        "aula": aula,
                    }
                )
        sesiones.delete_many({})
        if documentos:
            sesiones.insert_many(documentos)
        meta.replace_one(
            {"_id": "horario"},
            {
                "_id": "horario",
                "grupos": list(horario.grupos),
                "urls": horario.urls,
                "sincronizado_en": momento,
            },
            upsert=True,
        )

    def obtener_horario(self) -> HorarioPublicoEsiiab | None:
        meta = self.base_datos.coleccion("esiiab_meta").find_one({"_id": "horario"})
        if not meta:
            return None
        acumulado: dict[str, list[Sesion]] = {}
        for documento in self.base_datos.coleccion("esiiab_sesiones").find():
            nombre = documento["nombre_normalizado"]
            sesion: Sesion = (
                int(documento["dia"]),
                documento["inicio"],
                documento["fin"],
                documento["tipo"],
                documento.get("aula") or "",
                documento.get("grupo") or "",
            )
            acumulado.setdefault(nombre, []).append(sesion)
        return HorarioPublicoEsiiab(
            {nombre: tuple(sorted(sesiones)) for nombre, sesiones in acumulado.items()},
            dict(meta.get("urls") or {}),
            tuple(meta.get("grupos") or ()),
        )

    def sincronizado_en(self) -> datetime | None:
        meta = self.base_datos.coleccion("esiiab_meta").find_one({"_id": "horario"}, {"sincronizado_en": 1})
        if not meta or not meta.get("sincronizado_en"):
            return None
        valor = meta["sincronizado_en"]
        if isinstance(valor, datetime) and valor.tzinfo is None:
            return valor.replace(tzinfo=timezone.utc)
        return valor

    def guardar_ficha(self, ficha: FichaEsiiab) -> None:
        documento = {
            "codigo": ficha.codigo,
            "nombre": ficha.nombre,
            "nombre_normalizado": normalizar_texto(ficha.nombre),
            "url": ficha.url,
            "profesores": [
                {"nombre": profesor.nombre, "url": profesor.url, "tutorias": list(profesor.tutorias)}
                for profesor in ficha.profesores
            ],
            "actualizado_en": datetime.now(timezone.utc),
        }
        coleccion = self.base_datos.coleccion("esiiab_fichas")
        if ficha.codigo:
            documento["_id"] = ficha.codigo
            coleccion.replace_one({"_id": ficha.codigo}, documento, upsert=True)
        elif ficha.nombre:
            clave = normalizar_texto(ficha.nombre)
            documento["_id"] = clave
            coleccion.replace_one({"_id": clave}, documento, upsert=True)

    def obtener_ficha(self, codigo: str) -> FichaEsiiab | None:
        documento = self.base_datos.coleccion("esiiab_fichas").find_one({"_id": codigo})
        return _ficha_de(documento) if documento else None

    def obtener_ficha_por_nombre(self, nombre_normalizado: str) -> FichaEsiiab | None:
        documento = self.base_datos.coleccion("esiiab_fichas").find_one({"nombre_normalizado": nombre_normalizado})
        return _ficha_de(documento) if documento else None


def _ficha_de(documento: dict) -> FichaEsiiab:
    profesores = tuple(
        ProfesorEsiiab(
            item.get("nombre") or "",
            item.get("url") or "",
            tuple(item.get("tutorias") or ()),
        )
        for item in documento.get("profesores") or ()
    )
    return FichaEsiiab(
        documento.get("codigo") or "",
        documento.get("nombre") or "",
        documento.get("url") or "",
        profesores,
    )
