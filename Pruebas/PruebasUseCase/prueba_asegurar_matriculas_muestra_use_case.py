from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas
from Servidor.Dominio.DominioServices.matriculas_muestra import EMAIL_LAURA
from Servidor.Dominio.DominioUseCases.asegurar_matriculas_muestra_use_case import (
    AsegurarMatriculasMuestraUseCase,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas_memoria import (
    RepositorioMatriculasMemoria,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios_memoria import (
    RepositorioUsuariosMemoria,
)


def prueba_el_arranque_no_crea_cuentas_ni_pisa_matriculas():
    usuarios = RepositorioUsuariosMemoria()
    matriculas = RepositorioMatriculasMemoria()
    hasher = HasherContrasenas(rondas=4)
    email = "ana@alu.uclm.es"
    matriculas.reemplazar_alumno(email, ["42305", "42331"], {"42305": "A", "42331": "B"})
    matriculas.sincronizar_calificaciones(email, {"42305": 7.5}, set())
    matriculas.guardar_intensificacion(email, "software")

    AsegurarMatriculasMuestraUseCase(usuarios, matriculas, hasher).ejecutar()

    assert matriculas.obtener_codigos(email) == ["42305", "42331"]
    assert matriculas.obtener_notas(email)["42305"] == 7.5
    assert matriculas.obtener_intensificacion(email) == "software"
    assert matriculas.obtener_grupos(email) == {"42305": "A", "42331": "B"}
    assert usuarios.obtener_por_email("alba@ejemplo.com") is None
    assert matriculas.obtener_codigos(EMAIL_LAURA) == []
