from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioQueries.listar_asignaturas_query import ListarAsignaturasQuery
from Servidor.Dominio.DominioUseCases.asegurar_catalogo_asignaturas_use_case import AsegurarCatalogoAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.listar_asignaturas_use_case import ListarAsignaturasUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas_memoria import RepositorioAsignaturasMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos_memoria import RepositorioCursosMemoria


def _catalogo():
    cursos = RepositorioCursosMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    AsegurarCatalogoAsignaturasUseCase(cursos, asignaturas).ejecutar()
    return cursos, asignaturas


def prueba_la_tabla_asignatura_reune_las_tablas_de_curso():
    cursos, asignaturas = _catalogo()
    codigos = {asignatura.codigo for asignatura in asignaturas.obtener_todas()}
    assert "42300" in codigos
    assert "42319" in codigos
    assert "42325" in codigos
    assert "42330" in codigos
    assert "42358" in codigos
    assert {asignatura.curso for asignatura in cursos.obtener("primero")} == {CursoAsignatura.PRIMERO}
    assert {asignatura.curso for asignatura in cursos.obtener("cuarto")} == {CursoAsignatura.CUARTO}


def prueba_asignatura_copia_lo_que_haya_en_la_tabla_del_curso():
    cursos, asignaturas = _catalogo()
    cursos.guardar(
        Asignatura(
            "42300",
            "Cálculo renombrado",
            "Renamed calculus",
            CursoAsignatura.PRIMERO,
            6,
            1,
        )
    )
    cursos.guardar(Asignatura("99999", "Taller de apoyo", "Support workshop", CursoAsignatura.SEGUNDO, 6, 1))
    AsegurarCatalogoAsignaturasUseCase(cursos, asignaturas).reconstruir()
    guardadas = {asignatura.codigo: asignatura for asignatura in asignaturas.obtener_todas()}
    assert guardadas["42300"].nombre == "Cálculo renombrado"
    assert guardadas["99999"].curso == CursoAsignatura.SEGUNDO


def prueba_la_busqueda_ignora_mayusculas_y_tildes():
    _, asignaturas = _catalogo()
    caso = ListarAsignaturasUseCase(asignaturas)
    assert [asignatura.codigo for asignatura in caso.ejecutar(ListarAsignaturasQuery("calculo"))] == ["42300"]
    software = {asignatura.codigo for asignatura in caso.ejecutar(ListarAsignaturasQuery("SOFTWARE"))}
    assert {"42314", "42324", "42330"} <= software
    todas = caso.ejecutar(ListarAsignaturasQuery(""))
    assert todas[0].codigo == "42300"
    assert todas[-1].codigo == "42399" 
