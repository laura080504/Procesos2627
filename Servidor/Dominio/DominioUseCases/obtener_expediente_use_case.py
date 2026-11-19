from __future__ import annotations

from dataclasses import dataclass

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioServices.curso_alumno import curso_del_alumno
from Servidor.Dominio.DominioServices.expediente_alumno import expediente_de
from Servidor.Dominio.DominioServices.matriculas_muestra import TramoCurso, asegurar_matricula_de, tramos_de
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas

# TODO(secretaría): cuando UCLM exponga API oficial de expediente, sustituir la
# entrada manual por importación autenticada y marcar el origen de cada nota.


@dataclass(frozen=True)
class AsignaturaExpediente:
    codigo: str
    nombre: str
    nombre_ingles: str
    curso: CursoAsignatura
    creditos: int
    cuatrimestre: int
    nota: float | None
    convalidada: bool


@dataclass(frozen=True)
class ExpedienteVista:
    curso: CursoAsignatura | None
    tramos: list[TramoCurso]
    calificadas: list[AsignaturaExpediente]
    pendientes: list[AsignaturaExpediente]
    creditos_aprobados: int
    creditos_convalidados: int
    media: float | None
    origen: str = "manual"


class ObtenerExpedienteUseCase:
    def __init__(
        self,
        repositorio_matriculas: RepositorioMatriculas,
        repositorio_asignaturas: RepositorioAsignaturas,
    ):
        self.repositorio_matriculas = repositorio_matriculas
        self.repositorio_asignaturas = repositorio_asignaturas

    def ejecutar(self, email: str) -> ExpedienteVista:
        asegurar_matricula_de(self.repositorio_matriculas, email)
        catalogo = self.repositorio_asignaturas.obtener_todas()
        notas = self.repositorio_matriculas.obtener_notas(email)
        convalidadas = self.repositorio_matriculas.obtener_convalidadas(email)
        return _vista_de(catalogo, notas, convalidadas)


def _vista_de(
    catalogo: list[Asignatura],
    notas: dict[str, float | None],
    convalidadas: set[str] | frozenset[str],
) -> ExpedienteVista:
    calificadas: list[AsignaturaExpediente] = []
    pendientes: list[AsignaturaExpediente] = []
    con_resultado: list[Asignatura] = []

    for asignatura in catalogo:
        convalidada = asignatura.codigo in convalidadas
        nota = None if convalidada else notas.get(asignatura.codigo)
        item = AsignaturaExpediente(
            asignatura.codigo,
            asignatura.nombre,
            asignatura.nombre_ingles,
            asignatura.curso,
            asignatura.creditos,
            asignatura.cuatrimestre,
            nota,
            convalidada,
        )
        if convalidada or nota is not None:
            calificadas.append(item)
            con_resultado.append(asignatura)
        else:
            pendientes.append(item)

    calificadas.sort(key=lambda item: (item.curso.value, item.codigo))
    pendientes.sort(key=lambda item: (item.curso.value, item.codigo))
    expediente = expediente_de(con_resultado, notas, convalidadas)
    return ExpedienteVista(
        curso_del_alumno(con_resultado) if con_resultado else None,
        tramos_de(con_resultado),
        calificadas,
        pendientes,
        expediente.creditos_aprobados,
        expediente.creditos_convalidados,
        expediente.media,
        "manual",
    )
