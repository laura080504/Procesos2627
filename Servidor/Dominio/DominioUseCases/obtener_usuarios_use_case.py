from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioQueries.obtener_usuarios_query import ObtenerUsuariosQuery
from Servidor.Dominio.DominioResults.usuario_listado import UsuarioListado
from Servidor.Dominio.DominioServices.curso_alumno import curso_del_alumno
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
        if query.solicitante_rol == Rol.PROFESOR:
            return self._alumnos_del_profesor(query.solicitante_email, usuarios)
        if query.solicitante_rol == Rol.SUPERADMINISTRADOR:
            return self._listado_secretaria(usuarios)
        return [UsuarioListado(usuario) for usuario in usuarios]

    def _alumnos_del_profesor(self, email_profesor: str, usuarios) -> list[UsuarioListado]:
        if self.repositorio_docencia is None or self.repositorio_matriculas is None:
            return []
        codigos_docencia = set(self.repositorio_docencia.obtener_codigos(email_profesor))
        if not codigos_docencia:
            return []
        catalogo = self._catalogo()
        por_codigo = {asignatura.codigo: asignatura for asignatura in catalogo}
        matriculas = self.repositorio_matriculas.obtener_codigos_por_email()
        listado = []
        for usuario in usuarios:
            if usuario.rol != Rol.USUARIO or usuario.estado == EstadoUsuario.ELIMINADO:
                continue
            asignaturas = codigos_docencia.intersection(matriculas.get(usuario.email, []))
            if not asignaturas:
                continue
            listado.append(
                UsuarioListado(
                    usuario,
                    sorted(asignaturas),
                    None,
                    curso_del_alumno([por_codigo[c] for c in asignaturas if c in por_codigo]),
                )
            )
        return listado

    def _listado_secretaria(self, usuarios) -> list[UsuarioListado]:
        """Listado ligero: sin códigos de asignatura ni notas."""
        catalogo = self._catalogo()
        por_codigo = {asignatura.codigo: asignatura for asignatura in catalogo}
        matriculas = (
            self.repositorio_matriculas.obtener_codigos_por_email()
            if self.repositorio_matriculas is not None
            else {}
        )
        alumnos = []
        otros = []
        for usuario in usuarios:
            if usuario.rol == Rol.USUARIO:
                if usuario.estado == EstadoUsuario.ELIMINADO:
                    continue
                codigos = matriculas.get(usuario.email, [])
                propias = [por_codigo[c] for c in codigos if c in por_codigo]
                alumnos.append(UsuarioListado(usuario, [], None, curso_del_alumno(propias)))
            else:
                otros.append(UsuarioListado(usuario))
        return alumnos + otros

    def _catalogo(self):
        if self.repositorio_asignaturas is None:
            return []
        return self.repositorio_asignaturas.obtener_todas()
