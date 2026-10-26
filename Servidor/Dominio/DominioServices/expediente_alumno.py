from dataclasses import dataclass

from Servidor.Dominio.DominioEntities.asignatura import Asignatura

NOTA_APROBADO = 5


@dataclass(frozen=True)
class ExpedienteAlumno:
    creditos_aprobados: int
    media: float | None


def expediente_de(asignaturas: list[Asignatura], notas: dict[str, float | None]) -> ExpedienteAlumno:
    creditos_aprobados = 0
    suma = 0.0
    pesos = 0
    for asignatura in asignaturas:
        nota = notas.get(asignatura.codigo)
        if nota is None:
            continue
        suma += nota * asignatura.creditos
        pesos += asignatura.creditos
        if nota >= NOTA_APROBADO:
            creditos_aprobados += asignatura.creditos
    media = round(suma / pesos, 2) if pesos else None
    return ExpedienteAlumno(creditos_aprobados, media)
