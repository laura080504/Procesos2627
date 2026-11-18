from dataclasses import dataclass

from Servidor.Dominio.DominioEntities.asignatura import Asignatura

NOTA_APROBADO = 5


@dataclass(frozen=True)
class ExpedienteAlumno:
    creditos_aprobados: int
    creditos_convalidados: int
    media: float | None


def expediente_de(
    asignaturas: list[Asignatura],
    notas: dict[str, float | None],
    convalidadas: set[str] | frozenset[str] | None = None,
) -> ExpedienteAlumno:
    """Créditos aprobados (nota >= 5 o convalidada); media solo de calificadas no convalidadas."""
    codigos_convalidados = frozenset(convalidadas or ())
    creditos_aprobados = 0
    creditos_convalidados = 0
    suma_ponderada = 0.0
    creditos_calificados = 0

    for asignatura in asignaturas:
        if asignatura.codigo in codigos_convalidados:
            # Convalidada: suma como aprobada y no entra en la media.
            creditos_aprobados += asignatura.creditos
            creditos_convalidados += asignatura.creditos
            continue

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
    return ExpedienteAlumno(creditos_aprobados, creditos_convalidados, media)
