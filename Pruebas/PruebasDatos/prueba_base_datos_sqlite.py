import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from Servidor.ApiRest.ApiRestDependencies.repositorio_dependencies import crear_repositorios
from Servidor.configuracion import Configuracion
from Servidor.Infraestructura.base_datos_sqlite import BaseDatosSqlite
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones_memoria import RepositorioRecuperacionesMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones_sqlite import RepositorioRecuperacionesSqlite
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones_memoria import RepositorioSesionesMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones_sqlite import RepositorioSesionesSqlite
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios_memoria import RepositorioUsuariosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios_sqlite import RepositorioUsuariosSqlite
from Servidor.Infraestructura.InfraestructuraMigraciones.migrador_sqlite import MigradorSqlite
from Servidor.Dominio.DominioEntities.recuperacion import Recuperacion
from Servidor.Dominio.DominioEntities.sesion import Sesion
from Servidor.Dominio.DominioEntities.usuario import Usuario


def _configuracion(motor: str, ruta: str) -> Configuracion:
    return Configuracion(
        duracion_sesion=timedelta(hours=1),
        cookie_segura=False,
        ruta_datos=ruta,
        motor_datos=motor,
    )


def prueba_usuarios_sesiones_y_recuperaciones_se_guardan_en_el_archivo(tmp_path):
    base_datos = BaseDatosSqlite(tmp_path / "aplicacion.db")
    usuarios = RepositorioUsuariosSqlite(base_datos)
    sesiones = RepositorioSesionesSqlite(base_datos)
    recuperaciones = RepositorioRecuperacionesSqlite(base_datos)
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


def prueba_la_migracion_inicial_no_se_repite_ni_borra_datos(tmp_path):
    ruta = tmp_path / "aplicacion.db"
    with sqlite3.connect(ruta) as conexion:
        conexion.execute("CREATE TABLE esquema_migraciones (version TEXT PRIMARY KEY, aplicada_en TEXT)")
    base_datos = BaseDatosSqlite(ruta)
    RepositorioUsuariosSqlite(base_datos).insertar(
        Usuario(email="laura@ejemplo.com", nick="laura", contrasena_hash="hash")
    )

    assert MigradorSqlite(ruta).aplicar() == []
    assert RepositorioUsuariosSqlite(BaseDatosSqlite(ruta)).obtener_por_email("laura@ejemplo.com").nick == "laura"

    with sqlite3.connect(ruta) as conexion:
        version = conexion.execute("PRAGMA user_version").fetchone()[0]
        tablas = {fila[0] for fila in conexion.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert version == 1
    assert "esquema_migraciones" not in tablas
    assert {"usuarios", "sesiones", "recuperaciones"} <= tablas


def prueba_las_migraciones_siguientes_tienen_que_encadenar(tmp_path):
    carpeta = tmp_path / "versiones"
    carpeta.mkdir()
    (carpeta / "001_inicial.sql").write_text("CREATE TABLE a (id INTEGER PRIMARY KEY);", encoding="utf-8")
    (carpeta / "002_siguiente.sql").write_text("CREATE TABLE b (id INTEGER PRIMARY KEY);", encoding="utf-8")
    ruta = tmp_path / "aplicacion.db"

    assert MigradorSqlite(ruta, carpeta).aplicar() == ["001_inicial", "002_siguiente"]
    assert MigradorSqlite(ruta, carpeta).aplicar() == []

    (carpeta / "004_salto.sql").write_text("CREATE TABLE d (id INTEGER PRIMARY KEY);", encoding="utf-8")
    with pytest.raises(ValueError):
        MigradorSqlite(ruta, carpeta).aplicar()

    with sqlite3.connect(ruta) as conexion:
        version = conexion.execute("PRAGMA user_version").fetchone()[0]
        tablas = {fila[0] for fila in conexion.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert version == 2
    assert tablas == {"a", "b"}


def prueba_el_motor_memoria_no_abre_el_archivo(tmp_path):
    usuarios, sesiones, recuperaciones = crear_repositorios(_configuracion("memoria", str(tmp_path / "no.db")))
    assert isinstance(usuarios, RepositorioUsuariosMemoria)
    assert isinstance(sesiones, RepositorioSesionesMemoria)
    assert isinstance(recuperaciones, RepositorioRecuperacionesMemoria)
    assert not (tmp_path / "no.db").exists()


def prueba_el_motor_sqlite_usa_el_archivo(tmp_path):
    ruta = tmp_path / "aplicacion.db"
    usuarios, sesiones, recuperaciones = crear_repositorios(_configuracion("sqlite", str(ruta)))
    assert isinstance(usuarios, RepositorioUsuariosSqlite)
    assert isinstance(sesiones, RepositorioSesionesSqlite)
    assert isinstance(recuperaciones, RepositorioRecuperacionesSqlite)
    assert ruta.exists()


def prueba_un_motor_desconocido_falla(tmp_path):
    with pytest.raises(ValueError):
        crear_repositorios(_configuracion("nube", str(tmp_path / "aplicacion.db")))
