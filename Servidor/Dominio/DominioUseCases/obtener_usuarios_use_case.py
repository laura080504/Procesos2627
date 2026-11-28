from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioQueries.obtener_usuarios_query import ObtenerUsuariosQuery
from Servidor.Dominio.DominioResults.usuario_listado import UsuarioListado
from Servidor.Dominio.DominioServices.expediente_alumno import expediente_de
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia import RepositorioDocencia
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios


class ObtenerUsuariosUseCase:
    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_matriculas: RepositorioMatriculas | None = None,
        repositorio_docencia: RepositorioDocencia | None = None,
        repositorio_asignaturas: RepositorioAsignaturas | None = None,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_matriculas = repositorio_matriculas
        self.repositorio_docencia = repositorio_docencia
        self.repositorio_asignaturas = repositorio_asignaturas

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
        catalogo = (
            self.repositorio_asignaturas.obtener_todas()
            if self.repositorio_asignaturas is not None
            else []
        )
        listado = []
        for usuario in usuarios:
            if usuario.rol != Rol.USUARIO or usuario.estado == EstadoUsuario.ELIMINADO:
                continue
            asignaturas = codigos_docencia.intersection(
                self.repositorio_matriculas.obtener_codigos(usuario.email)
            )
            if not asignaturas:
                continue
            notas = self.repositorio_matriculas.obtener_notas(usuario.email)
            convalidadas = self.repositorio_matriculas.obtener_convalidadas(usuario.email)
            media = expediente_de(catalogo, notas, convalidadas).media
            listado.append(UsuarioListado(usuario, sorted(asignaturas), media))
        return listado
