from datetime import datetime, timedelta, timezone

import mongomock
import pytest

from Servidor.ApiRest.ApiRestDependencies.repositorio_dependencies import crear_repositorios
from Servidor.configuracion import Configuracion
from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo, uri_con_credenciales
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones_memoria import (
    RepositorioRecuperacionesMemoria,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones_mongo import (
    RepositorioRecuperacionesMongo,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones_memoria import RepositorioSesionesMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones_mongo import RepositorioSesionesMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios_memoria import RepositorioUsuariosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from Servidor.Dominio.DominioEntities.recuperacion import Recuperacion
from Servidor.Dominio.DominioEntities.sesion import Sesion
from Servidor.Dominio.DominioEntities.usuario import Usuario


def _configuracion(motor: str, mongo_uri: str | None = None) -> Configuracion:
    return Configuracion(
        duracion_sesion=timedelta(hours=1),
        cookie_segura=False,
        motor_datos=motor,
        mongo_uri=mongo_uri,
    )


def _repositorios_mongo():
    base_datos = BaseDatosMongo(cliente=mongomock.MongoClient())
    return (
        RepositorioUsuariosMongo(base_datos),
        RepositorioSesionesMongo(base_datos),
        RepositorioRecuperacionesMongo(base_datos),
    )


def prueba_usuarios_sesiones_y_recuperaciones_se_guardan_en_mongo():
    usuarios, sesiones, recuperaciones = _repositorios_mongo()
    expira = datetime.now(timezone.utc) + timedelta(hours=1)

    laura = usuarios.insertar(Usuario(email="laura@ejemplo.com", nick="laura", contrasena_hash="hash"))
    assert usuarios.obtener_por_email(laura.email) == laura

    laura.nick = "laura2"
    usuarios.actualizar(laura)
    assert usuarios.obtener_todos()[0].nick == "laura2"

    sesiones.guardar(Sesion(token="token-sesion", email=laura.email, expira_en=expira))
    assert sesiones.obtener("token-sesion").email == laura.email
    sesiones.eliminar_por_email(laura.email)
    assert sesiones.obtener("token-sesion") is None

    recuperaciones.guardar(Recuperacion(token="token-recuperacion", email=laura.email, expira_en=expira))
    assert recuperaciones.obtener("token-recuperacion").email == laura.email
    recuperaciones.eliminar("token-recuperacion")
    assert recuperaciones.obtener("token-recuperacion") is None

    assert usuarios.eliminar(laura.email) is True
    assert usuarios.obtener_por_email(laura.email) is None


def prueba_el_motor_mongo_exige_uri():
    with pytest.raises(ValueError, match="MONGO_URI"):
        crear_repositorios(_configuracion("mongo"))


def prueba_cargar_configuracion_mongo_sin_uri_falla(monkeypatch):
    monkeypatch.setenv("DATOS_MOTOR", "mongo")
    monkeypatch.delenv("MONGO_URI", raising=False)
    from Servidor.configuracion import cargar_configuracion

    with pytest.raises(ValueError, match="MONGO_URI"):
        cargar_configuracion()


def prueba_el_motor_memoria_no_pide_mongo():
    usuarios, sesiones, recuperaciones = crear_repositorios(_configuracion("memoria"))
    assert isinstance(usuarios, RepositorioUsuariosMemoria)
    assert isinstance(sesiones, RepositorioSesionesMemoria)
    assert isinstance(recuperaciones, RepositorioRecuperacionesMemoria)


def prueba_un_motor_desconocido_falla():
    with pytest.raises(ValueError):
        crear_repositorios(_configuracion("nube"))


def prueba_uri_inyecta_usuario_y_contrasena():
    uri = uri_con_credenciales(
        "mongodb+srv://cluster0.ejemplo.mongodb.net/?appName=Cluster0",
        "usuario",
        "clave/especial",
    )
    assert uri == (
        "mongodb+srv://usuario:clave%2Fespecial@cluster0.ejemplo.mongodb.net/?appName=Cluster0"
    )


def prueba_uri_no_pisa_credenciales_ya_incluidas():
    original = "mongodb+srv://ya:clave@cluster0.ejemplo.mongodb.net/"
    assert uri_con_credenciales(original, "otro", "otra") == original


def prueba_cargar_configuracion_mongo_sin_credenciales_falla(monkeypatch):
    monkeypatch.setenv("DATOS_MOTOR", "mongo")
    monkeypatch.setenv("MONGO_URI", "mongodb+srv://cluster0.ejemplo.mongodb.net/")
    monkeypatch.delenv("MONGO_USUARIO", raising=False)
    monkeypatch.delenv("MONGO_CONTRASENA", raising=False)
    from Servidor.configuracion import cargar_configuracion

    with pytest.raises(ValueError, match="MONGO_USUARIO"):
        cargar_configuracion()
