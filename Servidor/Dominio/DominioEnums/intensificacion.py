from enum import StrEnum


class Intensificacion(StrEnum):
    SOFTWARE = "software"
    COMPUTADORES = "computadores"
    COMPUTACION = "computacion"
    TECNOLOGIAS_INFORMACION = "tecnologias_informacion"


def intensificacion_desde(valor: str | None) -> Intensificacion | None:
    if not valor:
        return None
    try:
        return Intensificacion(valor.strip().lower())
    except ValueError:
        return None
