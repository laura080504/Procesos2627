from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas
from Servidor.Dominio.DominioServices.matriculas_muestra import (
    ALUMNOS_PRUEBA,
    CONTRASENA_PRUEBA,
    forzar_matricula_laura,
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
        forzar_matricula_laura(self.repositorio_matriculas)
        for alumno in ALUMNOS_PRUEBA:
            email = alumno["email"]
            if self.repositorio_usuarios.obtener_por_email(email) is None:
                self.repositorio_usuarios.insertar(
                    Usuario(
                        email=email,
                        nick=alumno["nick"],
                        contrasena_hash=self.hasher.hashear(CONTRASENA_PRUEBA),
                    )
                )
