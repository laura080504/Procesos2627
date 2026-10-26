from Servidor.Dominio.DominioQueries.obtener_marcas_calendario_query import ObtenerMarcasCalendarioQuery
from Servidor.Dominio.DominioUseCases.asegurar_catalogo_asignaturas_use_case import AsegurarCatalogoAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.asegurar_eventos_muestra_use_case import AsegurarEventosMuestraUseCase
from Servidor.Dominio.DominioUseCases.obtener_marcas_calendario_use_case import ObtenerMarcasCalendarioUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas_memoria import RepositorioAsignaturasMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos_memoria import RepositorioCursosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos_memoria import RepositorioEventosMemoria


def _octubre():
    cursos = RepositorioCursosMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    eventos = RepositorioEventosMemoria()
    AsegurarCatalogoAsignaturasUseCase(cursos, asignaturas).ejecutar()
    AsegurarEventosMuestraUseCase(eventos, asignaturas).ejecutar()
    marcas = ObtenerMarcasCalendarioUseCase(eventos, asignaturas).ejecutar(ObtenerMarcasCalendarioQuery(2026, 10))
    return {marca.dia: [simbolo.tipo for simbolo in marca.simbolos] for marca in marcas}, marcas


def prueba_octubre_lista_cinco_examenes_y_pone_las_estrellas_delante():
    por_dia, marcas = _octubre()
    assert por_dia[11] == ["estrella"] * 5
    assert por_dia[16] == ["estrella", "estrella", "punto"]
    assert por_dia[27] == ["estrella", "punto", "punto"]
    assert por_dia[7] == ["punto"]
    assert len(por_dia) < 20
    assert all(simbolo.codigo and simbolo.nombre for marca in marcas for simbolo in marca.simbolos)


def prueba_otro_mes_no_repite_las_marcas_de_octubre():
    cursos = RepositorioCursosMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    eventos = RepositorioEventosMemoria()
    AsegurarCatalogoAsignaturasUseCase(cursos, asignaturas).ejecutar()
    AsegurarEventosMuestraUseCase(eventos, asignaturas).ejecutar()
    noviembre = ObtenerMarcasCalendarioUseCase(eventos, asignaturas).ejecutar(ObtenerMarcasCalendarioQuery(2026, 11))
    assert noviembre
    assert {marca.dia for marca in noviembre} != {4, 7, 11, 16, 21, 27}
