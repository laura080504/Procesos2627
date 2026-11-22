from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioQueries.obtener_usuarios_query import ObtenerUsuariosQuery
from Servidor.Dominio.DominioResults.usuario_listado import UsuarioListado
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia import RepositorioDocencia
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios


class ObtenerUsuariosUseCase:
    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_matriculas: RepositorioMatriculas | None = None,
        repositorio_docencia: RepositorioDocencia | None = None,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_matriculas = repositorio_matriculas
        self.repositorio_docencia = repositorio_docencia

    def ejecutar(self, query: ObtenerUsuariosQuery) -> list[UsuarioListado]:
        usuarios = self.repositorio_usuarios.obtener_todos()
        if query.solicitante_rol != Rol.PROFESOR:
            return [UsuarioListado(usuario) for usuario in usuarios]
        if self.repositorio_docencia is None or self.repositorio_matriculas is None:
            return []

        # Un profesor solo ve alumnado matriculado en las asignaturas que imparte.
        codigos_docencia = set(self.repositorio_docencia.obtener_codigos(query.solicitante_email))
        if not codigos_docencia:
            return []
        listado = []
        for usuario in usuarios:
            if usuario.rol != Rol.USUARIO or usuario.estado == EstadoUsuario.ELIMINADO:
                continue
            asignaturas = codigos_docencia.intersection(
                self.repositorio_matriculas.obtener_codigos(usuario.email)
            )
            if asignaturas:
                listado.append(UsuarioListado(usuario, sorted(asignaturas)))
        return listado
