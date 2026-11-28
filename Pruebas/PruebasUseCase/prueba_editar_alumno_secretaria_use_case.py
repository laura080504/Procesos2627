from datetime import datetime, timedelta, timezone

import pytest

from Servidor.Dominio.DominioEntities.sesion import Sesion
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioUseCases.editar_alumno_secretaria_use_case import EditarAlumnoSecretariaUseCase


def _use_case(repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones, repositorio_matriculas):
    return EditarAlumnoSecretariaUseCase(
        repositorio_usuarios,
        repositorio_sesiones,
        repositorio_recuperaciones,
        repositorio_matriculas,
    )


def prueba_secretaria_cambia_el_correo_y_conserva_sesion_y_matricula(
    repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones, repositorio_matriculas
):
    repositorio_usuarios.insertar(Usuario(email="alumno@ejemplo.com", nick="ana", contrasena_hash="x"))
    repositorio_sesiones.guardar(
        Sesion(
            "token-sesion",
            "alumno@ejemplo.com",
            datetime.now(timezone.utc) + timedelta(hours=1),
        )
    )
    repositorio_matriculas.reemplazar_alumno("alumno@ejemplo.com", ["42330"], {"42330": "A"})
    use_case = _use_case(
        repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones, repositorio_matriculas
    )

    guardado = use_case.ejecutar(
        "alumno@ejemplo.com",
        "nueva@ejemplo.com",
        "Ana",
        Rol.SUPERADMINISTRADOR,
    )

    assert guardado.email == "nueva@ejemplo.com"
    assert guardado.nick == "Ana"
    assert repositorio_usuarios.obtener_por_email("alumno@ejemplo.com") is None
    assert repositorio_sesiones.obtener("token-sesion").email == "nueva@ejemplo.com"
    assert repositorio_matriculas.obtener_codigos("nueva@ejemplo.com") == ["42330"]
    assert repositorio_matriculas.obtener_codigos("alumno@ejemplo.com") == []


def prueba_un_profesor_no_edita_a_un_alumno(
    repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones, repositorio_matriculas
):
    repositorio_usuarios.insertar(Usuario(email="alumno@ejemplo.com", nick="ana", contrasena_hash="x"))
    use_case = _use_case(
        repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones, repositorio_matriculas
    )
    with pytest.raises(PermisoInsuficiente):
        use_case.ejecutar("alumno@ejemplo.com", "alumno@ejemplo.com", "Ana", Rol.PROFESOR)
