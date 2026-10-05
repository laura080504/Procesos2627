import pytest
from fastapi.testclient import TestClient

from pruebas.datos_prueba import CONTRASENA
from servidor.api_rest.dependencies.repositorio_dependencies import (
    obtener_repositorio_recuperaciones,
    obtener_repositorio_sesiones,
    obtener_repositorio_usuarios,
)
from servidor.api_rest.dependencies.servicio_dependencies import obtener_hasher_contrasenas
from servidor.aplicacion import aplicacion
from servidor.datos.repositories.repositorio_recuperaciones_memoria import RepositorioRecuperacionesMemoria
from servidor.datos.repositories.repositorio_sesiones_memoria import RepositorioSesionesMemoria
from servidor.datos.repositories.repositorio_usuarios_memoria import RepositorioUsuariosMemoria
from servidor.logica.entities.usuario import Usuario
from servidor.logica.services.hasher_contrasenas import HasherContrasenas


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
def cliente(repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones, hasher):
    aplicacion.dependency_overrides[obtener_repositorio_usuarios] = lambda: repositorio_usuarios
    aplicacion.dependency_overrides[obtener_repositorio_sesiones] = lambda: repositorio_sesiones
    aplicacion.dependency_overrides[obtener_repositorio_recuperaciones] = lambda: repositorio_recuperaciones
    aplicacion.dependency_overrides[obtener_hasher_contrasenas] = lambda: hasher
    with TestClient(aplicacion) as cliente:
        yield cliente
    aplicacion.dependency_overrides.clear()


@pytest.fixture
def cliente_autenticado(cliente, usuario_registrado):
    respuesta = cliente.post(
        "/api/auth/inicio-sesion",
        json={"email": usuario_registrado.email, "contrasena": CONTRASENA},
    )
    assert respuesta.status_code == 200
    return cliente
