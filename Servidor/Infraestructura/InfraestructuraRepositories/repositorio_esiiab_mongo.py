from __future__ import annotations

from datetime import date, datetime, timezone

from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto
from Servidor.Dominio.DominioServices.parser_calendario_esiiab import CalendarioAcademicoEsiiab, FechaAcademica
from Servidor.Dominio.DominioServices.parser_examenes_esiiab import ExamenEsiiab, ExamenesEsiiab
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
            for dia, inicio, fin, tipo, aula, grupo, cuatrimestre in franjas:
                documentos.append(
                    {
                        "_id": f"{nombre}|{cuatrimestre}|{grupo}|{dia}|{inicio}|{fin}|{tipo}|{aula}",
                        "nombre_normalizado": nombre,
                        "grupo": grupo,
                        "dia": dia,
                        "inicio": inicio,
                        "fin": fin,
                        "tipo": tipo,
                        "aula": aula,
                        "cuatrimestre": int(cuatrimestre or 0),
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
                int(documento.get("cuatrimestre") or 0),
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
                {
                    "nombre": profesor.nombre,
                    "url": profesor.url,
                    "tutorias_primer": list(profesor.tutorias_primer),
                    "tutorias_segundo": list(profesor.tutorias_segundo),
                    "tutorias": list(profesor.tutorias),
                }
                for profesor in ficha.profesores
            ],
            "tutorias_version": 2,
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
        if not documento or documento.get("tutorias_version", 0) < 2:
            return None
        return _ficha_de(documento)

    def obtener_ficha_por_nombre(self, nombre_normalizado: str) -> FichaEsiiab | None:
        documento = self.base_datos.coleccion("esiiab_fichas").find_one({"nombre_normalizado": nombre_normalizado})
        if not documento or documento.get("tutorias_version", 0) < 2:
            return None
        return _ficha_de(documento)

    def guardar_calendario(
        self, calendario: CalendarioAcademicoEsiiab, sincronizado_en: datetime | None = None
    ) -> None:
        momento = sincronizado_en or datetime.now(timezone.utc)
        coleccion = self.base_datos.coleccion("esiiab_calendario")
        meta = self.base_datos.coleccion("esiiab_meta")
        documentos = [
            {
                "_id": f"{fecha.tipo}|{fecha.inicio.isoformat()}|{fecha.fin.isoformat()}|{fecha.titulo}",
                "tipo": fecha.tipo,
                "titulo": fecha.titulo,
                "inicio": fecha.inicio.isoformat(),
                "fin": fecha.fin.isoformat(),
            }
            for fecha in calendario.fechas
        ]
        coleccion.delete_many({})
        if documentos:
            coleccion.insert_many(documentos)
        meta.replace_one(
            {"_id": "calendario"},
            {"_id": "calendario", "curso": calendario.curso, "sincronizado_en": momento},
            upsert=True,
        )

    def obtener_calendario(self) -> CalendarioAcademicoEsiiab | None:
        meta = self.base_datos.coleccion("esiiab_meta").find_one({"_id": "calendario"})
        documentos = list(self.base_datos.coleccion("esiiab_calendario").find())
        if not meta and not documentos:
            return None
        fechas = tuple(
            FechaAcademica(
                documento.get("tipo") or "academico",
                documento.get("titulo") or "",
                date.fromisoformat(documento["inicio"]),
                date.fromisoformat(documento["fin"]),
            )
            for documento in documentos
            if documento.get("inicio") and documento.get("fin")
        )
        return CalendarioAcademicoEsiiab(fechas, (meta or {}).get("curso") or "")

    def calendario_sincronizado_en(self) -> datetime | None:
        return _meta_momento(self.base_datos, "calendario")

    def guardar_examenes(self, examenes: ExamenesEsiiab, sincronizado_en: datetime | None = None) -> None:
        momento = sincronizado_en or datetime.now(timezone.utc)
        coleccion = self.base_datos.coleccion("esiiab_examenes")
        meta = self.base_datos.coleccion("esiiab_meta")
        documentos = [
            {
                "_id": (
                    f"{examen.convocatoria}|{examen.fecha.isoformat()}|{examen.hora}|"
                    f"{normalizar_texto(examen.nombre)}"
                ),
                "nombre": examen.nombre,
                "nombre_normalizado": normalizar_texto(examen.nombre),
                "fecha": examen.fecha.isoformat(),
                "hora": examen.hora,
                "centro": examen.centro,
                "aulas": examen.aulas,
                "convocatoria": examen.convocatoria,
            }
            for examen in examenes.examenes
        ]
        coleccion.delete_many({})
        if documentos:
            coleccion.insert_many(documentos)
        meta.replace_one(
            {"_id": "examenes"},
            {"_id": "examenes", "sincronizado_en": momento, "total": len(documentos)},
            upsert=True,
        )

    def obtener_examenes(self) -> ExamenesEsiiab | None:
        meta = self.base_datos.coleccion("esiiab_meta").find_one({"_id": "examenes"})
        documentos = list(self.base_datos.coleccion("esiiab_examenes").find())
        if not meta and not documentos:
            return None
        examenes = tuple(
            ExamenEsiiab(
                documento.get("nombre") or "",
                date.fromisoformat(documento["fecha"]),
                documento.get("hora") or "",
                documento.get("centro") or "",
                documento.get("aulas") or "",
                documento.get("convocatoria") or "ordinaria",
            )
            for documento in documentos
            if documento.get("fecha")
        )
        return ExamenesEsiiab(examenes)

    def examenes_sincronizado_en(self) -> datetime | None:
        return _meta_momento(self.base_datos, "examenes")


def _meta_momento(base_datos: BaseDatosMongo, clave: str) -> datetime | None:
    meta = base_datos.coleccion("esiiab_meta").find_one({"_id": clave}, {"sincronizado_en": 1})
    if not meta or not meta.get("sincronizado_en"):
        return None
    valor = meta["sincronizado_en"]
    if isinstance(valor, datetime) and valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor


def _ficha_de(documento: dict) -> FichaEsiiab:
    profesores = tuple(_profesor_de(item) for item in documento.get("profesores") or ())
    return FichaEsiiab(
        documento.get("codigo") or "",
        documento.get("nombre") or "",
        documento.get("url") or "",
        profesores,
    )


def _profesor_de(item: dict) -> ProfesorEsiiab:
    tiene_split = "tutorias_primer" in item or "tutorias_segundo" in item
    if not tiene_split:
        # Ficha antigua sin separar cuatrimestres: no inventar; se redescargará.
        return ProfesorEsiiab(item.get("nombre") or "", item.get("url") or "", (), ())
    return ProfesorEsiiab(
        item.get("nombre") or "",
        item.get("url") or "",
        tuple(item.get("tutorias_primer") or ()),
        tuple(item.get("tutorias_segundo") or ()),
    )
