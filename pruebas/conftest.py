import pytest
from fastapi.testclient import TestClient

from servidor.api_rest.dependencies import obtener_repositorio_usuarios
from servidor.aplicacion import aplicacion
from servidor.datos.repositories import RepositorioUsuariosMemoria


@pytest.fixture
def repositorio():
    return RepositorioUsuariosMemoria()


@pytest.fixture
def cliente(repositorio):
    aplicacion.dependency_overrides[obtener_repositorio_usuarios] = lambda: repositorio
    yield TestClient(aplicacion)
    aplicacion.dependency_overrides.clear()
