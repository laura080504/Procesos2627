import pytest

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioUseCases.asignar_delegado_use_case import AsignarDelegadoUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas_memoria import (
    RepositorioAsignaturasMemoria,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas_memoria import (
    RepositorioMatriculasMemoria,
)


def _use_case(repositorio_usuarios):
    asignaturas = RepositorioAsignaturasMemoria()
    asignaturas.reemplazar(
        [
            Asignatura("42300", "Calculo", "Calculus", CursoAsignatura.PRIMERO, 6, 1),
            Asignatura("42330", "Procesos", "Processes", CursoAsignatura.TERCERO, 6, 1),
            Asignatura("42327", "Algo", "Algo", CursoAsignatura.TERCERO, 6, 1),
        ]
    )
    matriculas = RepositorioMatriculasMemoria()
    return AsignarDelegadoUseCase(repositorio_usuarios, matriculas, asignaturas), matriculas


def prueba_asigna_delegado_del_curso_mayoritario(repositorio_usuarios, hasher):
    use_case, matriculas = _use_case(repositorio_usuarios)
    alumno = repositorio_usuarios.insertar(
        Usuario(email="alumno@ejemplo.com", nick="alumno", contrasena_hash=hasher.hashear("contrasena-segura"))
    )
    # Mayoría de tercero aunque quede una de primero.
    matriculas.reemplazar_alumno(alumno.email, ["42300", "42330", "42327"])
    guardado = use_case.ejecutar(alumno.email, Rol.SUPERADMINISTRADOR)
    assert guardado.delegado_curso == CursoAsignatura.TERCERO


def prueba_sin_mayoria_de_curso_no_asigna_delegado(repositorio_usuarios, hasher):
    use_case, matriculas = _use_case(repositorio_usuarios)
    alumno = repositorio_usuarios.insertar(
        Usuario(email="alumno@ejemplo.com", nick="alumno", contrasena_hash=hasher.hashear("contrasena-segura"))
    )
    matriculas.reemplazar_alumno(alumno.email, ["42300", "42330"])
    with pytest.raises(EstadoNoValido):
        use_case.ejecutar(alumno.email, Rol.SUPERADMINISTRADOR)


def prueba_no_permite_segundo_delegado_del_mismo_curso(repositorio_usuarios, hasher):
    use_case, matriculas = _use_case(repositorio_usuarios)
    primero = repositorio_usuarios.insertar(
        Usuario(email="uno@ejemplo.com", nick="uno", contrasena_hash=hasher.hashear("contrasena-segura"))
    )
    segundo = repositorio_usuarios.insertar(
        Usuario(email="dos@ejemplo.com", nick="dos", contrasena_hash=hasher.hashear("contrasena-segura"))
    )
    matriculas.reemplazar_alumno(primero.email, ["42330", "42327"])
    matriculas.reemplazar_alumno(segundo.email, ["42330", "42327"])
    use_case.ejecutar(primero.email, Rol.SUPERADMINISTRADOR)
    with pytest.raises(EstadoNoValido, match="ya tiene un delegado"):
        use_case.ejecutar(segundo.email, Rol.SUPERADMINISTRADOR)


def prueba_profesor_no_asigna_delegado(repositorio_usuarios, hasher):
    use_case, matriculas = _use_case(repositorio_usuarios)
    alumno = repositorio_usuarios.insertar(
        Usuario(email="alumno@ejemplo.com", nick="alumno", contrasena_hash=hasher.hashear("contrasena-segura"))
    )
    matriculas.reemplazar_alumno(alumno.email, ["42330", "42327"])
    with pytest.raises(PermisoInsuficiente):
        use_case.ejecutar(alumno.email, Rol.PROFESOR)
