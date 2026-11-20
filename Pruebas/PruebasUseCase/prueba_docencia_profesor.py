from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioServices.docencia_muestra import (
    CODIGOS_GALLUD,
    EMAIL_GALLUD,
    NOMBRE_GALLUD,
    asegurar_docencia_muestra,
    asegurar_rol_profesor_gallud,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios_memoria import (
    RepositorioUsuariosMemoria,
)
from Servidor.Dominio.DominioServices.franjas_tutorias import franjas_tutorias_de
from Servidor.Dominio.DominioServices.parser_ficha_esiiab import FichaEsiiab, ProfesorEsiiab
from Servidor.Dominio.DominioUseCases.asegurar_catalogo_asignaturas_use_case import AsegurarCatalogoAsignaturasUseCase
from Servidor.Dominio.DominioUseCases.obtener_matricula_use_case import ObtenerMatriculaUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas_memoria import RepositorioAsignaturasMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos_memoria import RepositorioCursosMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia_memoria import RepositorioDocenciaMemoria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas_memoria import RepositorioMatriculasMemoria


class _ClienteFichaGallud:
    def urls_asignaturas(self):
        return {}

    def fichas_de(self, pares):
        fichas = {}
        for codigo, nombre in pares:
            fichas[codigo] = FichaEsiiab(
                codigo,
                nombre,
                "",
                (
                    ProfesorEsiiab(
                        NOMBRE_GALLUD,
                        "",
                        ("Lunes: 10:00 - 12:00", "Miércoles: 16:00 - 18:00"),
                        ("Martes: 09:00 - 11:00",),
                    ),
                ),
            )
        return fichas


def _catalogo():
    cursos = RepositorioCursosMemoria()
    asignaturas = RepositorioAsignaturasMemoria()
    AsegurarCatalogoAsignaturasUseCase(cursos, asignaturas).ejecutar()
    return asignaturas


def prueba_asegura_docencia_gallud():
    docencia = RepositorioDocenciaMemoria()
    asegurar_docencia_muestra(docencia)
    assert docencia.obtener_codigos(EMAIL_GALLUD) == list(CODIGOS_GALLUD)
    assert docencia.obtener_nombre_docente(EMAIL_GALLUD) == NOMBRE_GALLUD
    asegurar_docencia_muestra(docencia)
    assert docencia.obtener_codigos(EMAIL_GALLUD) == list(CODIGOS_GALLUD)


def prueba_gallud_deja_de_ser_superadministrador():
    usuarios = RepositorioUsuariosMemoria()
    usuarios.insertar(
        Usuario(
            email=EMAIL_GALLUD,
            nick="admin",
            contrasena_hash="x",
            rol=Rol.SUPERADMINISTRADOR,
        )
    )
    asegurar_rol_profesor_gallud(usuarios)
    assert usuarios.obtener_por_email(EMAIL_GALLUD).rol == Rol.PROFESOR


def prueba_franjas_tutorias_parsea_dias_y_horas():
    franjas = franjas_tutorias_de(
        "42330",
        "Procesos",
        "Processes",
        ("Lunes: 10:00 - 12:00", "Miércoles: 16:00–18:00"),
    )
    assert [(f.dia, f.inicio, f.fin, f.tipo) for f in franjas] == [
        (1, "10:00", "12:00", "tutoria"),
        (3, "16:00", "18:00", "tutoria"),
    ]


def prueba_admin_ve_solo_asignaturas_impartidas_y_horario_del_cuatri():
    asignaturas = _catalogo()
    matriculas = RepositorioMatriculasMemoria()
    docencia = RepositorioDocenciaMemoria()
    asegurar_docencia_muestra(docencia)
    resultado = ObtenerMatriculaUseCase(
        matriculas,
        asignaturas,
        _ClienteFichaGallud(),
        docencia,
    ).ejecutar(EMAIL_GALLUD)

    assert resultado.modo == "profesor"
    assert resultado.nombre_docente == NOMBRE_GALLUD
    assert {a.codigo for a in resultado.asignaturas} == set(CODIGOS_GALLUD)
    assert resultado.cuatrimestre_actual == 1
    # Ambos cuatrimestres viajan en horario; el cliente elige según la semana.
    del_primero = [franja for franja in resultado.horario if franja.cuatrimestre == 1]
    del_segundo = [franja for franja in resultado.horario if franja.cuatrimestre == 2]
    assert any(franja.codigo == "42330" and franja.tipo != "tutoria" for franja in del_primero)
    assert any(franja.codigo == "42327" for franja in del_segundo)
    assert all(franja.codigo != "42327" for franja in del_primero)
    tutorias = [franja for franja in del_primero if franja.tipo == "tutoria"]
    assert tutorias
    assert all(franja.codigo == "42330" for franja in tutorias)
    assert {(franja.dia, franja.inicio) for franja in tutorias} == {(1, "10:00"), (3, "16:00")}
    # Las tutorías del 2.º cuatrimestre viajan igual: la agenda las pinta al navegar allí.
    tutorias_segundo = [franja for franja in del_segundo if franja.tipo == "tutoria"]
    assert tutorias_segundo
    assert all(franja.codigo == "42327" for franja in tutorias_segundo)
    assert {(franja.dia, franja.inicio) for franja in tutorias_segundo} == {(2, "09:00")}
    # La agenda no repite la misma franja aunque la publiquen dos asignaturas.
    claves = [
        (franja.cuatrimestre, franja.dia, franja.inicio, franja.fin)
        for franja in resultado.horario
        if franja.tipo == "tutoria"
    ]
    assert len(claves) == len(set(claves))
    # Ficha: tutorías del cuatrimestre real (PC), no de la semana navegada.
    procesos = next(a for a in resultado.asignaturas if a.codigo == "42330")
    assert procesos.profesores
    assert any("10:00" in linea for linea in procesos.profesores[0].tutorias)


class _ClienteFichaSoloPrimerCuatrimestre:
    """Caso real de ESIIAB: publica las tutorías solo en el bloque del primer cuatrimestre."""

    def urls_asignaturas(self):
        return {}

    def fichas_de(self, pares):
        return {
            codigo: FichaEsiiab(
                codigo,
                nombre,
                "",
                (ProfesorEsiiab(NOMBRE_GALLUD, "", ("Lunes: 11:00 - 13:00",), ()),),
            )
            for codigo, nombre in pares
        }


def prueba_tutorias_publicadas_en_el_bloque_equivocado_van_a_su_cuatrimestre():
    asignaturas = _catalogo()
    matriculas = RepositorioMatriculasMemoria()
    docencia = RepositorioDocenciaMemoria()
    asegurar_docencia_muestra(docencia)
    resultado = ObtenerMatriculaUseCase(
        matriculas,
        asignaturas,
        _ClienteFichaSoloPrimerCuatrimestre(),
        docencia,
    ).ejecutar(EMAIL_GALLUD)

    tutorias = [franja for franja in resultado.horario if franja.tipo == "tutoria"]
    primer_cuatri = {(franja.dia, franja.inicio) for franja in tutorias if franja.cuatrimestre == 1}
    segundo_cuatri = {(franja.dia, franja.inicio) for franja in tutorias if franja.cuatrimestre == 2}
    assert primer_cuatri == {(1, "11:00")}
    # Diseño de Software es del 2.º cuatrimestre: su tutoría no se pinta en el 1.º.
    assert segundo_cuatri == {(1, "11:00")}
    assert all(franja.codigo == "42330" for franja in tutorias if franja.cuatrimestre == 1)
    assert all(franja.codigo == "42327" for franja in tutorias if franja.cuatrimestre == 2)
