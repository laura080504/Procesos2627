from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado
from Servidor.Dominio.DominioUseCases.asegurar_catalogo_asignaturas_use_case import (
    AsegurarCatalogoAsignaturasUseCase,
)
from Servidor.Dominio.DominioUseCases.obtener_horario_alumno_use_case import ObtenerHorarioAlumnoUseCase
from Servidor.Dominio.DominioUseCases.obtener_matricula_use_case import ObtenerMatriculaUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas_memoria import (
    RepositorioAsignaturasMemoria,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos_memoria import RepositorioCursosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia_memoria import RepositorioDocenciaMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas_memoria import (
    RepositorioMatriculasMemoria,
)

import pytest


def _caso(repositorio_usuarios):
    profesor = repositorio_usuarios.insertar(
        Usuario(email="profesor@ejemplo.com", nick="profesor", contrasena_hash="x", rol=Rol.PROFESOR)
    )
    propio = repositorio_usuarios.insertar(
        Usuario(email="alumno@ejemplo.com", nick="alumno", contrasena_hash="x")
    )
    ajeno = repositorio_usuarios.insertar(
        Usuario(email="ajeno@ejemplo.com", nick="ajeno", contrasena_hash="x")
    )
    secretaria = repositorio_usuarios.insertar(
        Usuario(
            email="super@ejemplo.com",
            nick="super",
            contrasena_hash="x",
            rol=Rol.SUPERADMINISTRADOR,
        )
    )
    docencia = RepositorioDocenciaMemoria()
    matriculas = RepositorioMatriculasMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    AsegurarCatalogoAsignaturasUseCase(RepositorioCursosMemoria(), asignaturas).ejecutar()
    docencia.reemplazar(profesor.email, ["42300"])
    matriculas.reemplazar_alumno(propio.email, ["42300"], {"42300": "A"})
    matriculas.reemplazar_alumno(ajeno.email, ["42302"], {"42302": "A"})
    caso = ObtenerHorarioAlumnoUseCase(
        repositorio_usuarios,
        matriculas,
        docencia,
        asignaturas,
        ObtenerMatriculaUseCase(matriculas, asignaturas),
    )
    return caso, profesor, propio, ajeno, secretaria


def prueba_un_profesor_obtiene_el_horario_de_su_alumno(repositorio_usuarios):
    caso, profesor, propio, _, _ = _caso(repositorio_usuarios)
    resultado = caso.ejecutar(profesor.email, Rol.PROFESOR, propio.email)
    assert resultado.horario
    assert {franja.codigo for franja in resultado.horario} == {"42300"}
    assert any(
        franja.dia == 4 and franja.inicio == "08:15" and franja.tipo == "teoria"
        for franja in resultado.horario
    )


def prueba_un_profesor_no_ve_el_horario_de_un_alumno_ajeno(repositorio_usuarios):
    caso, profesor, _, ajeno, _ = _caso(repositorio_usuarios)
    with pytest.raises(PermisoInsuficiente):
        caso.ejecutar(profesor.email, Rol.PROFESOR, ajeno.email)


def prueba_un_alumno_no_consulta_horarios_ajenos(repositorio_usuarios):
    caso, _, propio, ajeno, _ = _caso(repositorio_usuarios)
    with pytest.raises(PermisoInsuficiente):
        caso.ejecutar(propio.email, Rol.USUARIO, ajeno.email)
    with pytest.raises(PermisoInsuficiente):
        caso.ejecutar(propio.email, Rol.USUARIO, propio.email)


def prueba_secretaria_obtiene_el_horario_de_cualquier_alumno(repositorio_usuarios):
    caso, _, _, ajeno, secretaria = _caso(repositorio_usuarios)
    resultado = caso.ejecutar(secretaria.email, Rol.SUPERADMINISTRADOR, ajeno.email)
    assert any(franja.codigo == "42302" for franja in resultado.horario)


def prueba_horario_de_alumno_inexistente_es_404(repositorio_usuarios):
    caso, profesor, _, _, secretaria = _caso(repositorio_usuarios)
    with pytest.raises(UsuarioNoEncontrado):
        caso.ejecutar(profesor.email, Rol.PROFESOR, "nadie@ejemplo.com")
    with pytest.raises(UsuarioNoEncontrado):
        caso.ejecutar(secretaria.email, Rol.SUPERADMINISTRADOR, "nadie@ejemplo.com")
