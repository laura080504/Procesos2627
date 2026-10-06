import pytest
from fastapi.testclient import TestClient

from servidor.api_rest.dependencies.configuracion_dependencies import obtener_hasher_contrasenas
from servidor.api_rest.dependencies.repositorio_dependencies import (
    obtener_repositorio_recuperaciones,
    obtener_repositorio_sesiones,
    obtener_repositorio_usuarios,
)
from servidor.aplicacion import aplicacion
from servidor.dominio.entities.usuario import Usuario
from servidor.dominio.enums.rol import Rol
from servidor.dominio.services.hasher_contrasenas import HasherContrasenas
from servidor.infraestructura.repositories.repositorio_recuperaciones_memoria import RepositorioRecuperacionesMemoria
from servidor.infraestructura.repositories.repositorio_sesiones_memoria import RepositorioSesionesMemoria
from servidor.infraestructura.repositories.repositorio_usuarios_memoria import RepositorioUsuariosMemoria

CONTRASENA = "contrasena-segura"


@pytest.fixture
def repositorio_usuarios():
    return RepositorioUsuariosMemoria()


@pytest.fixture
def repositorio_sesiones():
    return RepositorioSesionesMemoria()


@pytest.fixture
def repositorio_recuperaciones():
    return RepositorioRecuperacionesMemoria()


@pytest.fixture
def hasher():
    return HasherContrasenas(rondas=4)


@pytest.fixture
def usuario_registrado(repositorio_usuarios, hasher):
    return repositorio_usuarios.insertar(
        Usuario(email="laura@ejemplo.com", nick="laura", contrasena_hash=hasher.hashear(CONTRASENA))
    )


@pytest.fixture
def administrador(repositorio_usuarios, hasher):
    return repositorio_usuarios.insertar(
        Usuario(
            email="admin@ejemplo.com",
            nick="admin",
            contrasena_hash=hasher.hashear(CONTRASENA),
            rol=Rol.ADMINISTRADOR,
        )
    )


@pytest.fixture
def cliente(repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones, hasher):
    aplicacion.dependency_overrides[obtener_repositorio_usuarios] = lambda: repositorio_usuarios
    aplicacion.dependency_overrides[obtener_repositorio_sesiones] = lambda: repositorio_sesiones
    aplicacion.dependency_overrides[obtener_repositorio_recuperaciones] = lambda: repositorio_recuperaciones
    aplicacion.dependency_overrides[obtener_hasher_contrasenas] = lambda: hasher
    with TestClient(aplicacion) as cliente_http:
        yield cliente_http
    aplicacion.dependency_overrides.clear()


@pytest.fixture
def cliente_autenticado(cliente, usuario_registrado):
    respuesta = cliente.post(
        "/api/auth/inicio-sesion",
        json={"email": usuario_registrado.email, "contrasena": CONTRASENA},
    )
    assert respuesta.status_code == 200
    return cliente


@pytest.fixture
def cliente_administrador(cliente, administrador):
    respuesta = cliente.post(
        "/api/auth/inicio-sesion",
        json={"email": administrador.email, "contrasena": CONTRASENA},
    )
    assert respuesta.status_code == 200
    return cliente
