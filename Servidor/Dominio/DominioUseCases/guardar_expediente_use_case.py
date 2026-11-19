from __future__ import annotations

from dataclasses import dataclass

from Servidor.Dominio.DominioEnums.intensificacion import Intensificacion, intensificacion_desde
from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioUseCases.obtener_expediente_use_case import ExpedienteVista, ObtenerExpedienteUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas

# TODO(secretaría): bloquear edición manual de notas oficiales importadas.


@dataclass(frozen=True)
class CalificacionEntrada:
    codigo: str
    nota: float | None = None
    convalidada: bool = False


class GuardarExpedienteUseCase:
    def __init__(
        self,
        repositorio_matriculas: RepositorioMatriculas,
        repositorio_asignaturas: RepositorioAsignaturas,
        obtener_expediente: ObtenerExpedienteUseCase,
        invalidar_matricula=None,
    ):
        self.repositorio_matriculas = repositorio_matriculas
        self.repositorio_asignaturas = repositorio_asignaturas
        self.obtener_expediente = obtener_expediente
        self.invalidar_matricula = invalidar_matricula

    def ejecutar(
        self,
        email: str,
        calificaciones: list[CalificacionEntrada] | None = None,
        intensificacion: str | None = None,
        *,
        actualizar_calificaciones: bool = True,
    ) -> ExpedienteVista:
        catalogo = {asignatura.codigo for asignatura in self.repositorio_asignaturas.obtener_todas()}
        notas: dict[str, float | None] = {}
        convalidadas: set[str] = set()
        vistos: set[str] = set()

        if intensificacion is not None:
            valor = intensificacion.strip().lower()
            if valor and intensificacion_desde(valor) is None:
                raise EstadoNoValido("La intensificación no es válida.")
            self.repositorio_matriculas.guardar_intensificacion(email, valor or None)

        if not actualizar_calificaciones:
            if self.invalidar_matricula is not None:
                self.invalidar_matricula(email)
            return self.obtener_expediente.ejecutar(email)

        for item in calificaciones or []:
            codigo = (item.codigo or "").strip()
            if not codigo:
                raise EstadoNoValido("Cada calificación necesita un código de asignatura.")
            if codigo not in catalogo:
                raise EstadoNoValido(f"La asignatura {codigo} no está en el catálogo.")
            if codigo in vistos:
                raise EstadoNoValido(f"La asignatura {codigo} está repetida.")
            vistos.add(codigo)

            if item.convalidada:
                convalidadas.add(codigo)
                notas[codigo] = None
                continue

            if item.nota is None:
                raise EstadoNoValido(f"Indica la nota de {codigo} o márcala como convalidada.")

            try:
                nota = float(item.nota)
            except (TypeError, ValueError) as error:
                raise EstadoNoValido(f"La nota de {codigo} no es válida.") from error
            if nota < 0 or nota > 10:
                raise EstadoNoValido(f"La nota de {codigo} debe estar entre 0 y 10.")
            notas[codigo] = round(nota, 2)

        self.repositorio_matriculas.sincronizar_calificaciones(email, notas, convalidadas)
        if self.invalidar_matricula is not None:
            self.invalidar_matricula(email)
        return self.obtener_expediente.ejecutar(email)
