from datetime import date

import pytest

from Servidor.Dominio.DominioCommands.crear_aviso_secretaria_command import CrearAvisoSecretariaCommand
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioEnums.tipo_aviso_secretaria import TipoAvisoSecretaria
from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioServices.marcas_calendario import marcas_del_mes
from Servidor.Dominio.DominioUseCases.asegurar_avisos_secretaria_muestra_use_case import (
    AsegurarAvisosSecretariaMuestraUseCase,
)
from Servidor.Dominio.DominioUseCases.crear_aviso_secretaria_use_case import CrearAvisoSecretariaUseCase
from Servidor.Dominio.DominioUseCases.eliminar_aviso_secretaria_use_case import EliminarAvisoSecretariaUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_avisos_secretaria_memoria import (
    RepositorioAvisosSecretariaMemoria,
)


def prueba_siembra_avisos_esiiab_y_aparecen_en_marcas():
    repositorio = RepositorioAvisosSecretariaMemoria()
    AsegurarAvisosSecretariaMuestraUseCase(repositorio).ejecutar()
    avisos = repositorio.obtener_todos()
    assert len(avisos) >= 3
    marcas = marcas_del_mes([], {}, 2026, 5, avisos_secretaria=avisos)
    simbolos = [simbolo for marca in marcas for simbolo in marca.simbolos]
    assert any(simbolo.tipo == "secretaria" for simbolo in simbolos)
    assert any("Mercado de Trabajo" in simbolo.nombre for simbolo in simbolos)


def prueba_secretaria_crea_y_elimina_aviso():
    repositorio = RepositorioAvisosSecretariaMemoria()
    creado = CrearAvisoSecretariaUseCase(repositorio).ejecutar(
        CrearAvisoSecretariaCommand(
            titulo="Propuesta de tutoría abierta",
            tipo=TipoAvisoSecretaria.PROPUESTA,
            fecha=date(2026, 11, 30),
            hora="17:00",
            lugar="Aula 1.2",
            url="https://esiiab.uclm.es/eventos/",
            descripcion=None,
            solicitante_rol=Rol.SUPERADMINISTRADOR,
        )
    )
    assert creado.id
    assert repositorio.obtener_por_id(creado.id) is not None
    EliminarAvisoSecretariaUseCase(repositorio).ejecutar(creado.id, Rol.SUPERADMINISTRADOR)
    assert repositorio.obtener_por_id(creado.id) is None


def prueba_rechaza_un_enlace_que_no_es_http():
    repositorio = RepositorioAvisosSecretariaMemoria()
    with pytest.raises(EstadoNoValido):
        CrearAvisoSecretariaUseCase(repositorio).ejecutar(
            CrearAvisoSecretariaCommand(
                titulo="Enlace inválido",
                tipo=TipoAvisoSecretaria.AVISO,
                fecha=date(2026, 12, 1),
                hora="10:00",
                lugar=None,
                url="javascript:alert(1)",
                descripcion=None,
                solicitante_rol=Rol.SUPERADMINISTRADOR,
            )
        )


def prueba_profesor_no_crea_aviso_secretaria():
    repositorio = RepositorioAvisosSecretariaMemoria()
    with pytest.raises(PermisoInsuficiente):
        CrearAvisoSecretariaUseCase(repositorio).ejecutar(
            CrearAvisoSecretariaCommand(
                titulo="No válido",
                tipo=TipoAvisoSecretaria.AVISO,
                fecha=date(2026, 12, 1),
                hora="10:00",
                lugar=None,
                url=None,
                descripcion=None,
                solicitante_rol=Rol.PROFESOR,
            )
        )
