---
type: Proceso
title: Flujo, CI y despliegue
description: Cómo llega un cambio a main y qué hace el workflow de GitHub Actions (sprints 1 y 2).
timestamp: 2026-11-19
---

# Procesos

El resumen a seguir está en el [README](../README.md), sección «Flujo de trabajo (GitHub Flow)». Esto es lo que muestra el historial.

## Flujo de trabajo

La especificación pide una rama por cambio, pruebas locales con `pytest` y un pull request hacia `main`.

Comprobado el 2026-11-19 con `git log` / merges a `main`:

- **Sprint 1:** PR #1–#8 desde `Sprint-1`; #9 desde `Prueba-tecnica-sprint-1`. Tres merges `Merge branch 'Sprint-1'` sin PR: `9fdd9b1`, `afb9e67`, `5fb3380`. Alta del repo `91bd639` directa en `main`.
- **Sprint 2:** PR #10–#17 desde `sprint2` (y #12 desde `docs/okf-sprint1`). Todos integrados por pull request.
- `git tag` no devolvió etiquetas de hito.

Por verificar: protección de `main` en GitHub (exigir CI en verde / bloquear push directo).

## Integración continua

Archivo: `.github/workflows/ci.yml`.

Se dispara en `pull_request` y en `push` a `main`. El job `pruebas` usa Python 3.13, instala `requirements-dev.txt` y ejecuta `pytest`.

En el sprint 1, el PR #5 se integró con el paso de pruebas en rojo. En el tramo del sprint 2 (#10–#17) no consta en el historial un merge equivalente con CI en rojo. Las ejecuciones concretas se consultan en la pestaña Actions del repositorio.

## Despliegue continuo

El job `desplegar` declara `needs: pruebas` y solo corre si el evento es `push` a `main`. Publica en Cloud Run y escribe la URL en el resumen de la ejecución.

Variables que el workflow actualiza en el servicio: `DATOS_MOTOR` y `URL_PUBLICA`. El resto se configura en el servicio (nombres en el README; valores fuera del repositorio).

Primer commit de despliegue: `b0e7946` (2026-10-13). El CI existía desde `013c6f6` (2026-10-03).
