---
type: Proceso
title: Flujo, CI y despliegue
description: Cómo llega un cambio a main y qué hace el workflow de GitHub Actions.
timestamp: 2026-10-28
---

# Procesos

El resumen que hay que seguir está en el [README](../README.md), sección «Flujo de trabajo (GitHub Flow)». Esto es lo que muestra el historial.

## Flujo de trabajo

La especificación pide una rama por cambio, pruebas en local con `pytest` y un pull request hacia `main`.

Lo comprobado el 2026-10-28, sin `gh`, con la API pública de GitHub y con `git log`:

- 11 pull requests, todos con `merged_at`. Del #1 al #8 la rama de origen es `Sprint-1`. El #9 sale de `Prueba-tecnica-sprint-1`. El #10 y el #11 salen de `sprint2`.
- Tres commits de `main` son `Merge branch 'Sprint-1'` y no coinciden con el `merge_commit_sha` de ningún pull request: `9fdd9b1`, `afb9e67` y `5fb3380`. Ahí entraron el correo, Google, el despliegue y el cambio a la API de Brevo.
- El alta del repositorio (`91bd639`) está directo en `main`.
- `git tag` no devolvió etiquetas. Los cuatro hitos del apartado 10 de la especificación no están marcados.

Por verificar: la protección de `main` en GitHub (bloquear el push directo o exigir el CI en verde). En el historial hubo push que no es un merge de pull request, así que esa protección no estaba activa en esas fechas o no cubría esos merges.

## Integración continua

Archivo: `.github/workflows/ci.yml`.

Se dispara en `pull_request` y en `push` a `main`. El job `pruebas` instala `requirements-dev.txt` con Python 3.13 y ejecuta `pytest`.

La API de Actions, consultada el 2026-10-28, devolvió 24 ejecuciones: 21 `success` y 3 `failure`. Las tres fallaron en el paso «Ejecutar pruebas»:

- Pull request #5, el 2026-10-06, y el push a `main` de ese mismo merge. El pull request se integró igual. El detalle del fallo queda en esas ejecuciones; no se copia aquí.
- Un primer intento del pull request #11, el 2026-10-26. El despliegue de esa ejecución figura como `skipped`. Una ejecución posterior del pull request y el push a `main` terminaron en verde.

Por verificar: el mensaje concreto de cada fallo, en la pestaña Actions. No está resumido aquí porque no se leyeron las líneas del log.

## Despliegue continuo

El job `desplegar` declara `needs: pruebas` y solo corre si el evento es `push` a `main`. Publica el `Dockerfile` en Cloud Run (servicio y región en el propio workflow) y escribe la URL en el resumen de la ejecución.

Las variables que el workflow actualiza en el servicio son `DATOS_MOTOR` y `URL_PUBLICA`. El resto se configura en el servicio y el README dice que se conserva entre despliegues. El nombre del secreto de la cuenta de servicio está en el README; el valor no está en el repositorio.

La URL pública está en el README. El 2026-10-28 una petición HEAD respondió 200.

El primer commit de despliegue es `b0e7946` (2026-10-13), dentro del merge `9fdd9b1`. El CI ya existía el 2026-10-03 (commit `013c6f6`, primeras ejecuciones en verde ese día). El despliegue no esperó al primer día; a partir de ese workflow, un push a `main` con pruebas en rojo no despliega, porque el job depende de `pruebas`.
