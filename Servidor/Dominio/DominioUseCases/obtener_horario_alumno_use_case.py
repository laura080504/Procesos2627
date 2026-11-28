from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado
from Servidor.Dominio.DominioQueries.obtener_usuarios_query import ObtenerUsuariosQuery
from Servidor.Dominio.DominioUseCases.obtener_matricula_use_case import MatriculaAlumno, ObtenerMatriculaUseCase
from Servidor.Dominio.DominioUseCases.obtener_usuarios_use_case import ObtenerUsuariosUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia import RepositorioDocencia
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios


class ObtenerHorarioAlumnoUseCase:
    """Horario de un alumno visible para quien ya gestiona el listado.

    Secretaría ve a cualquier alumno. Un profesor solo a los matriculados en
    asignaturas que imparte (las mismas reglas que ObtenerUsuariosUseCase).
    Un alumno no puede consultar el horario de otra cuenta por esta vía.
    """

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_matriculas: RepositorioMatriculas,
        repositorio_docencia: RepositorioDocencia,
        repositorio_asignaturas: RepositorioAsignaturas,
        obtener_matricula: ObtenerMatriculaUseCase,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_matriculas = repositorio_matriculas
        self.repositorio_docencia = repositorio_docencia
        self.repositorio_asignaturas = repositorio_asignaturas
        self.obtener_matricula = obtener_matricula

    def ejecutar(self, solicitante_email: str, solicitante_rol: Rol, email_alumno: str) -> MatriculaAlumno:
        if solicitante_rol not in (Rol.PROFESOR, Rol.SUPERADMINISTRADOR):
            raise PermisoInsuficiente()

        email = email_alumno.strip().lower()
        usuario = self.repositorio_usuarios.obtener_por_email(email)
        if usuario is None or usuario.estado == EstadoUsuario.ELIMINADO:
            raise UsuarioNoEncontrado(email)
        if usuario.rol != Rol.USUARIO:
            raise PermisoInsuficiente()

        if solicitante_rol == Rol.PROFESOR and not self._alumno_visible(solicitante_email, email):
            raise PermisoInsuficiente()

        return self.obtener_matricula.ejecutar(email, "")

    def _alumno_visible(self, email_profesor: str, email_alumno: str) -> bool:
        listado = ObtenerUsuariosUseCase(
            self.repositorio_usuarios,
            self.repositorio_matriculas,
            self.repositorio_docencia,
            self.repositorio_asignaturas,
        ).ejecutar(
            ObtenerUsuariosQuery(
                solicitante_rol=Rol.PROFESOR,
                solicitante_email=email_profesor.strip().lower(),
            )
        )
        return any(item.usuario.email == email_alumno for item in listado)
