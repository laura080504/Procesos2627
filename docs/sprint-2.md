---
type: Sprint
title: Sprint 2
description: Agenda del estudiante, horario ESIIAB, matrículas y cierre de requisitos parciales del sprint 1.
timestamp: 2026-11-19
---

# Sprint 2

## Objetivo

Entregar la **agenda del estudiante** sobre la base del sprint 1: listado de asignaturas, horario semanal cruzado con la ESIIAB, marcas de calendario (exámenes, entregas, festivos), matrícula de muestra y roles de gestión (profesor / superadministrador), manteniendo CI y despliegue en `main`.

`main` al cierre: merge del [pull request #17](https://github.com/laura080504/Procesos2627/pull/17) (`5b63fc0`, 2026-11-18). Rama de trabajo: `sprint2`.

Tablero Donetonic: Por verificar: URL no está en el repositorio.

## Entregas (por pull request)

### Agenda, horario y roles — PR [#11](https://github.com/laura080504/Procesos2627/pull/11)

**Qué se hizo.** Vista de agenda, horario ESIIAB, matrícula, marcas y roles `profesor` / `superadministrador` (commit `46ad00b`, merge `77202eb`, 2026-10-26).

**Desviaciones.** Misma rama larga `sprint2` para varios cambios posteriores.

### Acceso Google — PR [#10](https://github.com/laura080504/Procesos2627/pull/10)

**Qué se hizo.** Alinear login y mostrar Google con sus colores. Merge `769d3c5` (2026-10-20).

### Bundle OKF sprint 1 — PR [#12](https://github.com/laura080504/Procesos2627/pull/12)

**Qué se hizo.** Añadir `docs/` OKF en el repositorio. Merge `1e9848d` (2026-10-28). El PR #17 la sacó del árbol; se volvió a versionar en `docs/` para cumplir la entrega en GitHub.

### Marcas de calendario — PR [#13](https://github.com/laura080504/Procesos2627/pull/13)

**Qué se hizo.** Hora y aula en cada marca. Merge `35d3a7c` (2026-10-28).

### Matrículas — PR [#14](https://github.com/laura080504/Procesos2627/pull/14)

**Qué se hizo.** Matrículas de muestra y asegurar matrícula al alta. Merge `27e2ec1` (2026-11-16).

### Correo y cuentas — PR [#15](https://github.com/laura080504/Procesos2627/pull/15) y [#16](https://github.com/laura080504/Procesos2627/pull/16)

**Qué se hizo.** Envío Brevo (SMTP/API) y reactivación de cuentas eliminadas; API de Brevo con SMTP de reserva. Merges `cc52323` y `f55d46b`.

### Cierre de dominio y docs — PR [#17](https://github.com/laura080504/Procesos2627/pull/17)

**Qué se hizo.** Clarificar servicios de dominio, `.dockerignore` / `.gitignore`, y sacar gráficos y `docs/` del código. Merge `5b63fc0`. Commit `7f5d62a`.

## Requisitos del sprint 1 que quedaban parciales

Actualizados en [requisitos.md](requisitos.md) al cerrar el sprint 2:

| ID | Resolución en sprint 2 |
|----|------------------------|
| RF-07, RF-08, RF-09 | Se asume [D-11](decisiones.md#d-11-tres-roles): profesor y superadministrador sustituyen al administrador único de la especificación. Estado **hecho** con esa decisión documentada. |
| PRO-01 | Sigue **parcial**: la rama `sprint2` concentra varios PR; no hay etiqueta por hito. Mejoró el uso exclusivo de pull requests hacia `main` en el tramo #10–#17. |
| PRO-02 | **hecho** en el tramo del sprint 2: los merges #10–#17 no muestran integración con CI en rojo (a diferencia del #5 del sprint 1). El workflow sigue ejecutando `pytest` en PR y push a `main`. |

## Retrospectiva

### Hechos

- Pull requests integrados en el tramo de agenda/matrícula: #10, #11, #12, #13, #14, #15, #16, #17 (comprobado en `git log` / historial de merges a `main`).
- CI y despliegue Cloud Run siguen en `.github/workflows/ci.yml` tras las pruebas en verde.
- El 2026-11-19, en el árbol actual de `main`, `pytest -q` dio **164 passed, 1 failed** (`prueba_google_sin_configurar_avisa`). Por verificar: si al cierre exacto de #17 el recuento era distinto.
- La documentación OKF de los sprints 1 y 2 está en `docs/` del repositorio (PR #12; reintegrada tras el #17).

### Qué funcionó

TODO(alumno): ¿qué parte del sprint 2 (agenda, horario vivo, matrícula, PRs) te ahorró más tiempo?

### Qué cambiaría

TODO(alumno): ¿pasarías a una rama corta por feature en el sprint 3, y etiquetarías el cierre del sprint 2?
