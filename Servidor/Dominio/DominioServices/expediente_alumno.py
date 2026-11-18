from dataclasses import dataclass

from Servidor.Dominio.DominioEntities.asignatura import Asignatura

NOTA_APROBADO = 5


@dataclass(frozen=True)
class ExpedienteAlumno:
    creditos_aprobados: int
    media: float | None


def expediente_de(asignaturas: list[Asignatura], notas: dict[str, float | None]) -> ExpedienteAlumno:
    """Créditos solo de aprobadas; media ponderada de todas las calificadas (también suspensos)."""
    creditos_aprobados = 0
    suma_ponderada = 0.0
    creditos_calificados = 0

    for asignatura in asignaturas:
        nota = notas.get(asignatura.codigo)
        if nota is None:
            continue

        suma_ponderada += nota * asignatura.creditos
        creditos_calificados += asignatura.creditos
        if nota >= NOTA_APROBADO:
            creditos_aprobados += asignatura.creditos

    media = None
    if creditos_calificados:
        media = round(suma_ponderada / creditos_calificados, 2)
    return ExpedienteAlumno(creditos_aprobados, media)
