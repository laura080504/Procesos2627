import unicodedata


def normalizar_texto(texto: str) -> str:
    """Minúsculas sin acentos ni espacios de más, para comparar nombres."""
    descompuesto = unicodedata.normalize("NFD", texto.casefold().strip())
    sin_tildes = "".join(letra for letra in descompuesto if unicodedata.category(letra) != "Mn")
    return " ".join(sin_tildes.split())
