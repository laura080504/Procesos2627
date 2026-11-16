from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas
from Servidor.Dominio.DominioServices.matriculas_muestra import (
    ALUMNOS_PRUEBA,
    CODIGOS_LAURA,
    CONTRASENA_PRUEBA,
    EMAIL_LAURA,
    asegurar_matricula_de,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios


class AsegurarMatriculasMuestraUseCase:
    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_matriculas: RepositorioMatriculas,
        hasher: HasherContrasenas,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_matriculas = repositorio_matriculas
        self.hasher = hasher

    def ejecutar(self) -> None:
        self._asegurar_alumno(EMAIL_LAURA, "laura", CODIGOS_LAURA, crear_usuario=False)
        for alumno in ALUMNOS_PRUEBA:
            self._asegurar_alumno(alumno["email"], alumno["nick"], alumno["codigos"], crear_usuario=True)

    def _asegurar_alumno(self, email: str, nick: str, codigos: tuple[str, ...], crear_usuario: bool) -> None:
        if crear_usuario and self.repositorio_usuarios.obtener_por_email(email) is None:
            self.repositorio_usuarios.insertar(
                Usuario(email=email, nick=nick, contrasena_hash=self.hasher.hashear(CONTRASENA_PRUEBA))
            )
        asegurar_matricula_de(self.repositorio_matriculas, email, codigos)
