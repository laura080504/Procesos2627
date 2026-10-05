import pytest

from servidor.logica.commands.registrar_usuario_command import RegistrarUsuarioCommand
from servidor.logica.enums.estado_usuario import EstadoUsuario
from servidor.logica.enums.rol import Rol
from servidor.logica.exceptions.usuario_ya_existe import UsuarioYaExiste
from servidor.logica.use_cases.registrar_usuario_use_case import RegistrarUsuarioUseCase


@pytest.fixture
def use_case(repositorio_usuarios, hasher):
    return RegistrarUsuarioUseCase(repositorio_usuarios, hasher)


def prueba_registra_usuario_con_valores_por_defecto(use_case, repositorio_usuarios):
    usuario = use_case.ejecutar(RegistrarUsuarioCommand("laura@ejemplo.com", "laura", "contrasena-segura"))
    assert usuario.rol == Rol.USUARIO
    assert usuario.estado == EstadoUsuario.ACTIVO
    assert repositorio_usuarios.obtener_por_email("laura@ejemplo.com") == usuario


def prueba_la_contrasena_se_guarda_con_hash(use_case, hasher):
    usuario = use_case.ejecutar(RegistrarUsuarioCommand("laura@ejemplo.com", "laura", "contrasena-segura"))
    assert usuario.contrasena_hash != "contrasena-segura"
    assert hasher.verificar("contrasena-segura", usuario.contrasena_hash)


def prueba_normaliza_el_email(use_case):
    usuario = use_case.ejecutar(RegistrarUsuarioCommand("  Laura@Ejemplo.COM ", "laura", "contrasena-segura"))
    assert usuario.email == "laura@ejemplo.com"


def prueba_no_permite_email_duplicado(use_case):
    use_case.ejecutar(RegistrarUsuarioCommand("laura@ejemplo.com", "laura", "contrasena-segura"))
    with pytest.raises(UsuarioYaExiste):
        use_case.ejecutar(RegistrarUsuarioCommand("LAURA@ejemplo.com", "otra", "otra-contrasena"))
