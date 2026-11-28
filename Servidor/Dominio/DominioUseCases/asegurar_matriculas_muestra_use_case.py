class AsegurarMatriculasMuestraUseCase:
    """El arranque no crea cuentas ni reescribe matrículas. Las guarda el alumno."""

    def __init__(self, repositorio_usuarios, repositorio_matriculas, hasher):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_matriculas = repositorio_matriculas
        self.hasher = hasher

    def ejecutar(self) -> None:
        return
