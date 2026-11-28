from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioQueries.obtener_usuarios_query import ObtenerUsuariosQuery
from Servidor.Dominio.DominioUseCases.obtener_usuarios_use_case import ObtenerUsuariosUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia_memoria import RepositorioDocenciaMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas_memoria import RepositorioMatriculasMemoria


def prueba_inicialmente_no_hay_usuarios(repositorio_usuarios):
    assert ObtenerUsuariosUseCase(repositorio_usuarios).ejecutar(ObtenerUsuariosQuery()) == []


def prueba_devuelve_los_usuarios_guardados(repositorio_usuarios, usuario_registrado):
    usuarios = ObtenerUsuariosUseCase(repositorio_usuarios).ejecutar(ObtenerUsuariosQuery())
    assert [resultado.usuario for resultado in usuarios] == [usuario_registrado]
    assert usuarios[0].asignaturas == []


def _escenario(repositorio_usuarios):
    profesor = repositorio_usuarios.insertar(
        Usuario(email="profesor@ejemplo.com", nick="profesor", contrasena_hash="x", rol=Rol.PROFESOR)
    )
    de_su_asignatura = repositorio_usuarios.insertar(
        Usuario(email="alumno@ejemplo.com", nick="alumno", contrasena_hash="x")
    )
    de_otra_asignatura = repositorio_usuarios.insertar(
        Usuario(email="ajeno@ejemplo.com", nick="ajeno", contrasena_hash="x")
    )
    superadministrador = repositorio_usuarios.insertar(
        Usuario(
            email="super@ejemplo.com",
            nick="super",
            contrasena_hash="x",
            rol=Rol.SUPERADMINISTRADOR,
        )
    )
    docencia = RepositorioDocenciaMemoria()
    matriculas = RepositorioMatriculasMemoria()
    docencia.reemplazar(profesor.email, ["42330"])
    matriculas.reemplazar_alumno(de_su_asignatura.email, ["42330", "42327"])
    matriculas.reemplazar_alumno(de_otra_asignatura.email, ["42327"])
    return profesor, de_su_asignatura, de_otra_asignatura, superadministrador, docencia, matriculas


def prueba_un_profesor_solo_ve_alumnos_matriculados_en_sus_asignaturas(repositorio_usuarios):
    profesor, propio, _, _, docencia, matriculas = _escenario(repositorio_usuarios)
    usuarios = ObtenerUsuariosUseCase(repositorio_usuarios, matriculas, docencia).ejecutar(
        ObtenerUsuariosQuery(solicitante_rol=Rol.PROFESOR, solicitante_email=profesor.email)
    )
    assert [resultado.usuario.email for resultado in usuarios] == [propio.email]
    assert usuarios[0].asignaturas == ["42330"]


def prueba_un_profesor_sin_docencia_no_ve_alumnos(repositorio_usuarios):
    profesor, _, _, _, _, matriculas = _escenario(repositorio_usuarios)
    usuarios = ObtenerUsuariosUseCase(
        repositorio_usuarios, matriculas, RepositorioDocenciaMemoria()
    ).ejecutar(
        ObtenerUsuariosQuery(solicitante_rol=Rol.PROFESOR, solicitante_email=profesor.email)
    )
    assert usuarios == []


def prueba_un_profesor_no_ve_alumnos_eliminados(repositorio_usuarios):
    profesor, propio, _, _, docencia, matriculas = _escenario(repositorio_usuarios)
    propio.estado = EstadoUsuario.ELIMINADO
    repositorio_usuarios.actualizar(propio)
    usuarios = ObtenerUsuariosUseCase(repositorio_usuarios, matriculas, docencia).ejecutar(
        ObtenerUsuariosQuery(solicitante_rol=Rol.PROFESOR, solicitante_email=profesor.email)
    )
    assert usuarios == []


def prueba_el_superadministrador_ve_todos_los_usuarios(repositorio_usuarios):
    _, _, _, superadministrador, docencia, matriculas = _escenario(repositorio_usuarios)
    usuarios = ObtenerUsuariosUseCase(repositorio_usuarios, matriculas, docencia).ejecutar(
        ObtenerUsuariosQuery(
            solicitante_rol=Rol.SUPERADMINISTRADOR,
            solicitante_email=superadministrador.email,
        )
    )
    assert len(usuarios) == 4
