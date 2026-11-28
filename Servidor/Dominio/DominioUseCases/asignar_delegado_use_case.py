from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado
from Servidor.Dominio.DominioServices.curso_alumno import curso_del_alumno
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios


class AsignarDelegadoUseCase:
    """Marca a un alumno como único delegado del curso en el que está asignado."""

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_matriculas: RepositorioMatriculas,
        repositorio_asignaturas: RepositorioAsignaturas,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_matriculas = repositorio_matriculas
        self.repositorio_asignaturas = repositorio_asignaturas

    def ejecutar(self, email: str, solicitante_rol: Rol, activar: bool = True):
        if solicitante_rol != Rol.SUPERADMINISTRADOR:
            raise PermisoInsuficiente()
        email = email.strip().lower()
        usuario = self.repositorio_usuarios.obtener_por_email(email)
        if usuario is None or usuario.estado == EstadoUsuario.ELIMINADO:
            raise UsuarioNoEncontrado(email)
        if usuario.rol != Rol.USUARIO:
            raise PermisoInsuficiente()

        if not activar:
            usuario.delegado_curso = None
            self.repositorio_usuarios.actualizar(usuario)
            return self.repositorio_usuarios.obtener_por_email(email)

        curso = self._curso_de(email)
        if curso is None:
            raise EstadoNoValido("El alumno no tiene un curso asignado")

        for otro in self.repositorio_usuarios.obtener_todos():
            if otro.email == email or otro.delegado_curso != curso:
                continue
            raise EstadoNoValido("Este curso ya tiene un delegado")

        usuario.delegado_curso = curso
        self.repositorio_usuarios.actualizar(usuario)
        return self.repositorio_usuarios.obtener_por_email(email)

    def _curso_de(self, email: str) -> CursoAsignatura | None:
        codigos = set(self.repositorio_matriculas.obtener_codigos(email))
        propias = [
            asignatura
            for asignatura in self.repositorio_asignaturas.obtener_todas()
            if asignatura.codigo in codigos
        ]
        return curso_del_alumno(propias)
